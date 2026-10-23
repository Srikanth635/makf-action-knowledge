"""Verify SHA-256 of all bundled immutable resources against assembly manifest."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent
manifest=json.loads((root/'RESOURCE_SHA256.json').read_text())
errors=[]
for relative,expected in manifest.items():
    p=root/relative
    actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else 'MISSING'
    if actual != expected:errors.append(relative)
print(f"Verified {len(manifest)-len(errors)} of {len(manifest)} resources")
if errors:
    print('MISMATCH:',', '.join(errors))
    raise SystemExit(1)
