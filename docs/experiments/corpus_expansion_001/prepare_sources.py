"""Preserve bounded exact PDF-text excerpts; never run a model or rewrite source text."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare(downloads):
    downloads = Path(downloads)
    configurations = [
        dict(key='softgym', document_id='lin-etal-softgym-arxiv-2011.07215v2',
             title='SoftGym: Benchmarking Deep Reinforcement Learning for Deformable Object Manipulation',
             authors=['Xingyu Lin', 'Yufei Wang', 'Jake Olkin', 'David Held'], version='2011.07215v2',
             passages=[('pourwater-task', 'PourWater Pour a cup', 'StraightenRope', 'Section 4, Tasks'),
                       ('fluid-model', 'Fluids can naturally', 'Rope is modeled', 'Section 3, fluid model'),
                       ('pouring-variations', 'PourWater, PourWaterAmount: For this task,', 'The water is initially', 'Appendix, task variations')]),
        dict(key='fluidlab', document_id='xian-etal-fluidlab-arxiv-2303.02346v1',
             title='FluidLab: A Differentiable Environment for Benchmarking Complex Fluid Manipulation',
             authors=['Zhou Xian', 'Bo Zhu', 'Zhenjia Xu', 'Hsiao-Yu Tung', 'Antonio Torralba', 'Katerina Fragkiadaki', 'Chuang Gan'],
             version='2303.02346v1',
             passages=[('pouring-task', 'Fined Grained Pouring', 'Gathering (Easy & Hard)', 'Section 4.1, task details'),
                       ('trajectory-optimization', 'Sampling-based trajectory optimization CMA-ES', 'Sim-to-real transfer We additionally', 'Section 5.2, reported optimization results'),
                       ('pouring-loss', 'Transporting, Pouring, Gathering (Easy)', 'Mixing The goal', 'Appendix B.2, loss and reward')]),
    ]
    extractor = subprocess.run(['pdftotext', '-v'], capture_output=True, text=True, check=True).stderr.splitlines()[0]
    retrieval = {r['name']: r for r in json.loads((downloads / 'downloads.json').read_text())}
    records = []
    for cfg in configurations:
        pdf = downloads / (cfg['key'] + '.pdf')
        text_path = downloads / (cfg['key'] + '.txt')
        text = text_path.read_bytes().decode('utf-8')
        assert cfg['version'] in text[:400]
        record = {k: cfg[k] for k in ('document_id', 'title', 'authors', 'version')}
        record.update(evidence_origin='published_simulation', simulation_reproduced=False,
            bibliographic_uri='https://arxiv.org/abs/' + cfg['version'],
            retrieved_from=retrieval[cfg['key']]['url'],
            retrieved_at=datetime.fromtimestamp(pdf.stat().st_mtime, timezone.utc).isoformat(),
            pdf_sha256=sha(pdf.read_bytes()), extracted_text_sha256=sha(text_path.read_bytes()),
            text_extraction=extractor + '; default reading order; exact contiguous slices', passages=[])
        assert record['pdf_sha256'] == retrieval[cfg['key']]['sha256']
        document = dict(document_id=cfg['document_id'], title=cfg['title'],
                        uri=record['bibliographic_uri'], synthetic_demo=False, passages=[])
        for pid, start, stop, section in cfg['passages']:
            assert text.count(start) == 1, start
            a = text.index(start)
            b = text.index(stop, a)
            # Keep whitespace and extraction artifacts exactly, including any page break.
            excerpt = text[a:b]
            first, last = text[:a].count('\f') + 1, text[:b].count('\f') + 1
            locator = f"arXiv {cfg['version']}, {section}, PDF pages {first}-{last}"
            file = cfg['key'] + '-' + pid + '.txt'
            (HERE / file).write_bytes(excerpt.encode('utf-8'))
            record['passages'].append(dict(passage_id=pid, file=file, locator=locator,
                text_start=a, text_end=b, sha256=sha(excerpt.encode('utf-8'))))
            document['passages'].append(dict(passage_id=pid, text=excerpt, locator=locator))
        (HERE / (cfg['key'] + '-source.json')).write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
        records.append(record)
    (HERE / 'source-catalog.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    return records


if __name__ == '__main__':
    records = prepare(sys.argv[1])
    print('Prepared', len(records), 'sources and', sum(len(r['passages']) for r in records), 'exact passages')
