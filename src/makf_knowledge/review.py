"""Offline coverage of reviewer-selected evidence spans, not an entailment judge.

The caller supplies the original documents and required spans for a specific
claim. Requirements must be reviewed again whenever that claim changes.
"""


def evidence_coverage(candidate, documents, requirements):
    """Check whether asserts_claim citations cover each annotated source span.

    Ambiguous repeated quotes require explicit offsets. Whitespace gaps between
    adjacent quotations are allowed; missing non-whitespace text is not.
    Invalid annotations raise; invalid citations are reported as failures.
    """
    passages = {}
    for document in documents:
        for passage in document['passages']:
            key = (document['document_id'], passage['passage_id'])
            if key in passages:
                raise ValueError('Duplicate document/passage identity')
            passages[key] = passage['text']
    if not requirements:
        raise ValueError('Coverage requires reviewer-selected evidence spans')

    def locate(item):
        key = (item['document_id'], item['passage_id'])
        text = passages[key]
        quote = item['exact_quote']
        if not quote.strip():
            raise ValueError('Empty evidence quote')
        start, end = item.get('start_char'), item.get('end_char')
        if start is None and end is None:
            start = text.find(quote)
            if start < 0 or text.find(quote, start + 1) >= 0:
                raise ValueError('Quote absent or ambiguous without offsets')
            end = start + len(quote)
        if (type(start) is not int or type(end) is not int or
                not 0 <= start < end <= len(text) or text[start:end] != quote):
            raise ValueError('Invalid evidence offsets')
        return key, start, end

    required = [locate(item) for item in requirements]
    covered = {key: set() for key in passages}
    invalid = []
    for index, support in enumerate(candidate['source_support']):
        try:
            key, start, end = locate(support)
        except (KeyError, ValueError, TypeError):
            invalid.append(index)
            continue
        if support['support_role'] == 'asserts_claim':
            covered[key].update(range(start, end))
    missing = [i for i, (key, start, end) in enumerate(required)
               if any(not passages[key][j].isspace() and j not in covered[key]
                      for j in range(start, end))]
    return {'status': 'PASS' if not missing and not invalid else 'FAIL',
            'missing_requirement_indexes': missing,
            'invalid_support_indexes': invalid,
            'scope': 'Annotated evidence coverage only; no entailment or truth assessment.'}
