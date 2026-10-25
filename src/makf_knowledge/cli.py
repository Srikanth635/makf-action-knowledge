"""CLI for ontology inspection, E1/E2 extraction and local provisional RDF export."""
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
from .pipeline import extract
from .providers import FixtureProvider, OpenAIProvider, ProviderError
from .quality import OpenAIReviewer, review_and_revise


def source_arguments(parser):
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


def extraction_request(args):
    # Preserve exact CRLF/Unicode source offsets; read_text translates line endings.
    passage = SourcePassage(args.passage_id, args.text_file.read_bytes().decode('utf-8'), args.locator)
    document = SourceDocument(args.source_id, args.source_title, args.synthetic_demo,
                              (passage,), args.source_uri, args.doi)
    return ExtractionRequest(args.batch_id, (document,), args.profile,
                             tuple(args.perspective) if args.perspective else None)

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
    source_arguments(parser)
    parser.add_argument('--out',type=Path,help='Save prompt/schema JSON including source text')
    parser=sub.add_parser('extract',help='Run an explicitly selected provider and validate provisional candidates')
    source_arguments(parser)
    parser.add_argument('--provider',choices=('openai','fixture'),required=True)
    parser.add_argument('--model',help='Explicit OpenAI model ID; required for --provider openai')
    parser.add_argument('--fixture-file',type=Path,help='Raw E1 response for offline fixture transport')
    parser.add_argument('--api-key-env',default='MAKF_OPENAI_API_KEY',help='Credential variable NAME, never a key value')
    parser.add_argument('--max-output-tokens',type=int,default=6000)
    parser.add_argument('--timeout',type=float,default=60)
    parser.add_argument('--review-model',help='Optional OpenAI model for a separate evidence/scope/mapping review')
    parser.add_argument('--revise-once',action='store_true',help='Allow one revision and second review; requires --review-model')
    parser.add_argument('--select-reviewed',action='store_true',help='Save a separate subset of candidates passing every model review check')
    parser.add_argument('--out-dir',type=Path,required=True,help='New run directory; existing directories are not overwritten')
    parser=sub.add_parser('schema',help='Regenerate JSON Schema from the bundled LinkML subset')
    parser.add_argument('--out',type=Path,help='Output JSON schema; if omitted print to stdout')
    parser=sub.add_parser('export-rdf',help='Validate and save a local provisional RDF snapshot; requires the rdf extra')
    parser.add_argument('input',help='E1 JSON file or pouring/grasping synthetic example')
    parser.add_argument('--profile',default='pouring',help='pouring, grasping, or local profile YAML')
    parser.add_argument('--base-iri',required=True,help='Explicit HTTP(S) base for data identifiers; never fetched')
    parser.add_argument('--selection-file',type=Path,help='E2 selection/report.json (advisory model review only)')
    parser.add_argument('--reviewed-batch',type=Path,help='Original reviewed candidates.json; required with --selection-file')
    parser.add_argument('--out-dir',type=Path,required=True,help='New local bundle directory; never overwrite an existing directory')
    parser=sub.add_parser('export-quantitative-rdf',help='Export provisional quantitative evidence with scalar and SHACL checks')
    parser.add_argument('input',help='Quantitative JSON file or fluidlab')
    parser.add_argument('--base-iri',required=True)
    parser.add_argument('--out-dir',type=Path,required=True)
    parser=sub.add_parser('ontologies',help='List bundled ontology files and metadata')
    parser=sub.add_parser('validate-quantitative',help='Validate scalar quantitative evidence and report unresolved issues')
    parser.add_argument('input',help='Quantitative JSON file or fluidlab for the packaged published-source fixture')
    parser=sub.add_parser('class',help='Inspect direct OWL restrictions of an ontology class')
    parser.add_argument('term',help='e.g. paf:PouringKnowledgeFrame')
    parser=sub.add_parser('inventory',help='Display precomputed P1.1 inventory statistics')
    parser=sub.add_parser('doctor',help='Check packaged resources and synthetic validation')
    args=p.parse_args(argv)
    try:
        if args.command=='status':
            print_json({'package_version':__version__,'completed':['P1.1 ontology inventory','P1.2 pouring frame','P1.3 MAKF refactor and grasping smoke test','E1 schema, profiles, offline validator','E2.1 extraction interface and E2.2 deterministic prompt builder','E2.3 optional OpenAI and fixture transports','Request-bound parsing, validation and local quarantine runner','E3 local provisional RDF export with E1 and SHACL validation'],'not_implemented':['Scientific entailment and generalization assessment','Authenticated human RDF promotion and graph-store publication','TigerGraph runtime integration','OWL DL consistency check with resolved DUL'],'live_experiment':'See docs/experiments/e23_pouring/README.md for verified run status','bundled_official_DUL':False,'world_model_data_included':False})
        elif args.command=='validate':print_json(validate_file(resolved_input(args.input),resolved_profile(args.profile)))
        elif args.command=='guidance':
            result=build_context(resolved_profile(args.profile))
            if args.out:
                args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(f'Wrote {args.out}')
            else:print_json(result)
        elif args.command=='prompt':
            result = build_extraction_prompt(extraction_request(args)).to_dict()
            if args.out:
                args.out.parent.mkdir(parents=True,exist_ok=True)
                args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
                print(f'Wrote {args.out}')
            else:print_json(result)
        elif args.command=='extract':
            if args.out_dir.exists():
                raise ValueError('Choose a new --out-dir; existing runs are preserved')
            if (args.revise_once or args.select_reviewed) and not args.review_model:
                raise ValueError('--revise-once and --select-reviewed require --review-model')
            if args.review_model and args.provider != 'openai':
                raise ValueError('--review-model requires --provider openai')
            request = extraction_request(args)
            if args.provider == 'openai':
                if not args.model or args.fixture_file:
                    raise ValueError('OpenAI requires --model and cannot use --fixture-file')
                provider = OpenAIProvider(args.model, api_key_env=args.api_key_env,
                                          max_output_tokens=args.max_output_tokens, timeout=args.timeout)
            else:
                if not args.fixture_file or args.model:
                    raise ValueError('Fixture transport requires --fixture-file and cannot use --model')
                provider = FixtureProvider(args.fixture_file.read_bytes().decode('utf-8'))
            reviewer = None
            workflow = None
            try:
                result = extract(request, provider)
                result.save(args.out_dir)
                if args.review_model:
                    reviewer = OpenAIReviewer(args.review_model, api_key_env=args.api_key_env,
                        max_output_tokens=args.max_output_tokens, timeout=args.timeout)
                    workflow = review_and_revise(request, result, provider, reviewer, args.out_dir,
                                                 revise_once=args.revise_once, select_passed=args.select_reviewed)
            finally:
                if reviewer is not None:
                    reviewer.close()
                if isinstance(provider, OpenAIProvider):
                    provider.close()
            if workflow is not None:
                print_json({**workflow, 'out_dir': str(args.out_dir)})
                return 0 if workflow['status'] in {'quality_passed_provisional', 'model_reviewed_subset', 'abstained'} else 1
            print_json({'status': result.report['status'], 'out_dir': str(args.out_dir),
                        'candidate_count': result.report.get('candidate_count', 0),
                        'error_code': result.report.get('error_code')})
            return 0 if result.report['status'] in {'provisional', 'abstained'} else 1
        elif args.command=='export-rdf':
            from .publication import export_batch, read_json
            if args.out_dir.exists():
                raise ValueError('Choose a new --out-dir; existing RDF bundles are preserved')
            if bool(args.selection_file) != bool(args.reviewed_batch):
                raise ValueError('--selection-file and --reviewed-batch must be supplied together')
            result = export_batch(read_json(resolved_input(args.input)), base_iri=args.base_iri,
                profile=args.profile,
                selection=read_json(args.selection_file) if args.selection_file else None,
                reviewed_batch=read_json(args.reviewed_batch) if args.reviewed_batch else None)
            result.save(args.out_dir)
            manifest = json.loads(result.manifest_json)
            print_json({'status': 'exported_provisional', 'out_dir': str(args.out_dir),
                'candidate_count': manifest['candidate_count'], 'review_state': manifest['review_state'],
                'shacl_conforms': manifest['shacl_conforms']})
        elif args.command=='schema':
            schema=compile_schema(yaml.safe_load(resource_path('schema','makf_extraction.linkml.yaml').read_text()))
            if args.out:
                args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(schema,indent=2)+'\n',encoding='utf8');print(f'Wrote {args.out}')
            else:print_json(schema)
        elif args.command=='export-quantitative-rdf':
            from .publication import read_json
            from .quantitative_rdf import export_quantitative
            if args.out_dir.exists():
                raise ValueError('Existing quantitative RDF bundles are preserved; choose a new --out-dir')
            path = resource_path('quantitative','fluidlab.json') if args.input == 'fluidlab' else Path(args.input)
            result = export_quantitative(read_json(path),base_iri=args.base_iri)
            result.save(args.out_dir)
            manifest=json.loads(result.manifest_json)
            print_json({'status':'exported_pending','quantity_count':manifest['quantity_count'],
                'shacl_conforms':True,'out_dir':str(args.out_dir)})
        elif args.command=='validate-quantitative':
            from .publication import read_json
            from .quantitative import validate_quantitative
            path = resource_path('quantitative','fluidlab.json') if args.input == 'fluidlab' else Path(args.input)
            print_json(validate_quantitative(read_json(path)))
        elif args.command=='ontologies':print_json(list_ontologies())
        elif args.command=='class':print_json(describe_class(args.term))
        elif args.command=='inventory':print(resource_path('inventory','inventory_stats.json').read_text(),end='')
        elif args.command=='doctor':
            all_ont=list_ontologies()
            results={a:validate_file(example_path(a),profile_path(a)) for a in ('pouring','grasping')}
            print_json({'status':'PASS','ontology_files':len(all_ont),'ontology_triplets':sum(x['triples'] for x in all_ont),'example_validations':results,'limitations':'No remote OWL imports or formal DL reasoning, no LLM'})
        return 0
    except (ProviderError,ValidationError,ValueError,KeyError,OSError,yaml.YAMLError,json.JSONDecodeError) as ex:
        print(f'ERROR: {ex}',file=sys.stderr)
        return 1

def main():raise SystemExit(run())
