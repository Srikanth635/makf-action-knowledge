"""Explicit, bounded live extraction: one call per prepared research source."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

from makf_knowledge.extraction import ExtractionRequest, SourceDocument, SourcePassage
from makf_knowledge.pipeline import extract
from makf_knowledge.providers import OpenAIProvider

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=False, mode=0o700)

    def run(key):
        doc = json.loads((HERE / (key + '-source.json')).read_text())
        source = SourceDocument(doc['document_id'], doc['title'], doc['synthetic_demo'],
            tuple(SourcePassage(**p) for p in doc['passages']), doc['uri'])
        request = ExtractionRequest('corpus-expansion-001-' + key, (source,), 'pouring',
                                    ('procedural', 'applicability', 'observational'))
        provider = OpenAIProvider(args.model, max_output_tokens=6000, timeout=120)
        try:
            result = extract(request, provider)
            result.save(args.out_dir / key)
            summary = {'source': key, 'status': result.report['status'],
                       'candidate_count': result.report.get('candidate_count', 0),
                       'error_code': result.report.get('error_code')}
            print(json.dumps(summary), flush=True)
            return summary
        finally:
            provider.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        summaries = list(pool.map(run, ('softgym', 'fluidlab')))
    (args.out_dir / 'summary.json').write_text(json.dumps(summaries, indent=2) + '\n')


if __name__ == '__main__':
    main()
