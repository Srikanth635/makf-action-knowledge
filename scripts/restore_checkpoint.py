"""Verify or restore the portable 2026-10-25 artifact checkpoint without API calls."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / 'docs/checkpoints/2026-10-25/artifact-inventory.json'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--verify-only', action='store_true')
    mode.add_argument('--out-dir', type=Path, help='Parent directory for restored makf-*-runs directories')
    args = parser.parse_args()
    rows = json.loads(MANIFEST.read_text())['files']
    verified = restored = 0
    for row in rows:
        if row['disposition'] != 'preserved':
            continue
        relative = Path(row['repository_path'])
        original = Path(row['original_path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe repository path')
        destination = original.relative_to('/workspace')
        if '..' in destination.parts or not destination.parts[0].startswith('makf-'):
            raise ValueError('Unsafe original artifact path')
        source = REPO / relative
        if hashlib.sha256(source.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Checkpoint hash mismatch: ' + str(relative))
        verified += 1
        if args.out_dir is None:
            continue
        target = args.out_dir / destination
        if target.is_symlink():
            raise ValueError('Refusing a symbolic-link target: ' + str(target))
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != row['sha256']:
                raise FileExistsError('Refusing to overwrite different content: ' + str(target))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        restored += 1
    print(json.dumps({'verified_artifact_references': verified, 'restored_files': restored,
                      'dependency_and_download_caches_not_restored': sum(r['disposition'] != 'preserved' for r in rows)}, indent=2))


if __name__ == '__main__':
    main()
