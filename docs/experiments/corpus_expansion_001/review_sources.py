"""Explicit model review with at most one revision per already-saved source run."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path

from makf_knowledge.extraction import ExtractionRequest, SourceDocument, SourcePassage
from makf_knowledge.pipeline import ExtractionResult
from makf_knowledge.providers import OpenAIProvider
from makf_knowledge.quality import OpenAIReviewer, review_and_revise, select_reviewed

HERE = Path(__file__).resolve().parent


def load_result(directory):
    def load(name):
        path = directory / name
        return json.loads(path.read_text()) if path.exists() else None
    return ExtractionResult(report=load('report.json'), prompt=load('prompt.json'),
        raw_response=(directory / 'response.txt').read_text() if (directory / 'response.txt').exists() else None,
        batch=load('candidates.json'), transport_request=load('transport-request.json'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True)
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()

    def review(key):
        directory = args.run_dir / key
        doc = json.loads((HERE / (key + '-source.json')).read_text())
        source = SourceDocument(doc['document_id'], doc['title'], doc['synthetic_demo'],
            tuple(SourcePassage(**p) for p in doc['passages']), doc['uri'])
        request = ExtractionRequest('corpus-expansion-001-' + key, (source,), 'pouring',
                                    ('procedural', 'applicability', 'observational'))
        provider = OpenAIProvider(args.model, max_output_tokens=6000, timeout=120)
        reviewer = OpenAIReviewer(args.model, max_output_tokens=6000, timeout=120)
        try:
            summary = review_and_revise(request, load_result(directory), provider, reviewer,
                directory, revise_once=True, select_passed=True)
            # A whole-batch pass still needs an explicit content-bound selection artifact for E3.
            if summary['status'] == 'quality_passed_provisional':
                latest = directory / summary['selected_run']
                select_reviewed(load_result(latest), load_result(latest / 'quality-review'), latest / 'selection')
                summary['selection_dir'] = str((latest / 'selection').relative_to(directory))
            elif summary['status'] == 'model_reviewed_subset':
                summary['selection_dir'] = summary['selected_run']
            print(json.dumps({'source':key, **summary}), flush=True)
            return {'source':key, **summary}
        finally:
            reviewer.close()
            provider.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        summaries = list(pool.map(review, ('softgym', 'fluidlab')))
    (args.run_dir / 'review-summary.json').write_text(json.dumps(summaries, indent=2) + '\n')


if __name__ == '__main__':
    main()
