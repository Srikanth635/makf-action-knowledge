"""Offline CLI for ontology inspection, E1 validation and E2 prompt construction."""
import argparse
import json
import sys
from pathlib import Path
import yaml
from . import __version__
from .paths import RESOURCE_ROOT, example_path, profile_path, resource_path
from .validation import SemanticValidator, ValidationError, validate_file
from .schema import compile_schema
from .guidance import build_context
from .ontology import list_ontologies, describe_class
from .extraction import ExtractionRequest, SourceDocument, SourcePassage, build_extraction_prompt

def print_json(obj): print(json.dumps(obj,indent=2,ensure_ascii=False))

def resolved_input(value):
    if value in ('pouring','grasping'):return example_path(value)
    return Path(value)

def resolved_profile(value):
    if value in ('pouring','grasping'):return profile_path(value)
    return Path(value)

def run(argv=None):
    p=argparse.ArgumentParser(prog='makf',description='MAKF action knowledge and offline extraction prompts')
    p.add_argument('--version',action='version',version=__version__)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('status',help='Show capability and testing scope')
    parser=sub.add_parser('validate',help='Validate a candidate batch against the E1 schema and local OWL declarations')
    parser.add_argument('input',help='Path to extraction JSON, or pouring/grasping for synthetic example')
    parser.add_argument('--profile',default='pouring',help='pouring, grasping, or path to profile YAML')
    parser=sub.add_parser('guidance',help='Create an ontology-grounded vocabulary guidance JSON')
    parser.add_argument('--profile',default='pouring')
    parser.add_argument('--out',type=Path,help='Output JSON filename; if omitted print to stdout')
    parser=sub.add_parser('prompt',help='Build an E2 prompt artifact locally; no model call')
    parser.add_argument('--profile',default='pouring',help='pouring, grasping, or local profile YAML')
    parser.add_argument('--text-file',type=Path,required=True,help='User-supplied UTF-8 excerpt')
    parser.add_argument('--source-id',required=True)
    parser.add_argument('--source-title',required=True)
    parser.add_argument('--passage-id',default='excerpt-1')
    parser.add_argument('--batch-id',required=True)
    parser.add_argument('--source-uri')
    parser.add_argument('--doi')
    parser.add_argument('--locator')
    parser.add_argument('--synthetic-demo',action='store_true',help='Mark invented sample text explicitly')
    parser.add_argument('--perspective',action='append',help='Select a profile perspective; repeat as needed')
    parser.add_argument('--out',type=Path,help='Save prompt/schema JSON including source text')
    parser=sub.add_parser('schema',help='Regenerate JSON Schema from the bundled LinkML subset')
    parser.add_argument('--out',type=Path,help='Output JSON schema; if omitted print to stdout')
    parser=sub.add_parser('ontologies',help='List bundled ontology files and metadata')
    parser=sub.add_parser('class',help='Inspect direct OWL restrictions of an ontology class')
    parser.add_argument('term',help='e.g. paf:PouringKnowledgeFrame')
    parser=sub.add_parser('inventory',help='Display precomputed P1.1 inventory statistics')
    parser=sub.add_parser('doctor',help='Check packaged resources and synthetic validation')
    args=p.parse_args(argv)
    try:
        if args.command=='status':
            print_json({'package_version':__version__,'completed':['P1.1 ontology inventory','P1.2 pouring frame','P1.3 MAKF refactor and grasping smoke test','E1 schema, profiles, offline validator','E2.1 extraction interface and E2.2 deterministic prompt builder'],'not_implemented':['E2.3 provider transports and live LLM extraction','E2.4 response parsing and quarantine pipeline','E3 RDF populated candidates/SHACL','TigerGraph runtime integration','OWL DL consistency check with resolved DUL'],'bundled_official_DUL':False,'world_model_data_included':False})
        elif args.command=='validate':print_json(validate_file(resolved_input(args.input),resolved_profile(args.profile)))
        elif args.command=='guidance':
            result=build_context(resolved_profile(args.profile))
            if args.out:
                args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(f'Wrote {args.out}')
            else:print_json(result)
        elif args.command=='prompt':
            # read_text uses universal-newline translation; source offsets require
            # retaining CRLF and Unicode exactly as supplied instead.
            passage = SourcePassage(args.passage_id, args.text_file.read_bytes().decode('utf-8'), args.locator)
            document = SourceDocument(args.source_id, args.source_title, args.synthetic_demo,
                                      (passage,), args.source_uri, args.doi)
            request = ExtractionRequest(args.batch_id, (document,), args.profile,
                                        tuple(args.perspective) if args.perspective else None)
            result = build_extraction_prompt(request).to_dict()
            if args.out:
                args.out.parent.mkdir(parents=True,exist_ok=True)
                args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                print(f'Wrote {args.out}')
            else:print_json(result)
        elif args.command=='schema':
            schema=compile_schema(yaml.safe_load(resource_path('schema','makf_extraction.linkml.yaml').read_text()))
            if args.out:
                args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(schema,indent=2)+'\n',encoding='utf8');print(f'Wrote {args.out}')
            else:print_json(schema)
        elif args.command=='ontologies':print_json(list_ontologies())
        elif args.command=='class':print_json(describe_class(args.term))
        elif args.command=='inventory':print(resource_path('inventory','inventory_stats.json').read_text(),end='')
        elif args.command=='doctor':
            all_ont=list_ontologies()
            results={a:validate_file(example_path(a),profile_path(a)) for a in ('pouring','grasping')}
            print_json({'status':'PASS','ontology_files':len(all_ont),'ontology_triplets':sum(x['triples'] for x in all_ont),'example_validations':results,'limitations':'No remote OWL imports or formal DL reasoning, no LLM'})
        return 0
    except (ValidationError,ValueError,KeyError,OSError,yaml.YAMLError,json.JSONDecodeError) as ex:
        print(f'ERROR: {ex}',file=sys.stderr)
        return 1

def main():raise SystemExit(run())
