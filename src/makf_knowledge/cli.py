"""Small, offline-first CLI for the P1.1–E1 research artifacts."""
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

def print_json(obj): print(json.dumps(obj,indent=2,ensure_ascii=False))

def resolved_input(value):
    if value in ('pouring','grasping'):return example_path(value)
    return Path(value)

def resolved_profile(value):
    if value in ('pouring','grasping'):return profile_path(value)
    return Path(value)

def run(argv=None):
    p=argparse.ArgumentParser(prog='makf',description='MAKF multiperspective action knowledge toolset (P1.1–E1)')
    p.add_argument('--version',action='version',version=__version__)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('status',help='Show capability and testing scope')
    parser=sub.add_parser('validate',help='Validate a candidate batch against the E1 schema and local OWL declarations')
    parser.add_argument('input',help='Path to extraction JSON, or pouring/grasping for synthetic example')
    parser.add_argument('--profile',default='pouring',help='pouring, grasping, or path to profile YAML')
    parser=sub.add_parser('guidance',help='Create an ontology-grounded vocabulary guidance JSON')
    parser.add_argument('--profile',default='pouring')
    parser.add_argument('--out',type=Path,help='Output JSON filename; if omitted print to stdout')
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
            print_json({'package_version':__version__,'completed':['P1.1 ontology inventory','P1.2 pouring frame','P1.3 MAKF refactor and grasping smoke test','E1 schema, profiles, offline validator'],'not_implemented':['E2 live LLM extraction','E3 RDF populated candidates/SHACL','TigerGraph runtime integration','OWL DL consistency check with resolved DUL'],'bundled_official_DUL':False,'world_model_data_included':False})
        elif args.command=='validate':print_json(validate_file(resolved_input(args.input),resolved_profile(args.profile)))
        elif args.command=='guidance':
            result=build_context(resolved_profile(args.profile))
            if args.out:
                args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(f'Wrote {args.out}')
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
    except (ValidationError,ValueError,KeyError,FileNotFoundError,yaml.YAMLError,json.JSONDecodeError) as ex:
        print(f'ERROR: {ex}',file=sys.stderr)
        return 1

def main():raise SystemExit(run())
