"""Fetch only pinned smoke inputs, verify Git/SHA-256 hashes and apply the recorded patch."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import urllib.request

HERE=Path(__file__).resolve().parent


def prepare(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    source=directory/'source';source.mkdir()
    manifest=json.loads((HERE/'source-manifest.json').read_text())
    def get(item):
        path=Path(item['path'])
        if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe manifest path')
        url=f"https://raw.githubusercontent.com/zhouxian/FluidLab/{manifest['commit']}/{path.as_posix()}"
        with urllib.request.urlopen(url,timeout=45) as response:data=response.read()
        assert hashlib.sha256(data).hexdigest()==item['sha256'],str(path)
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['git_blob'],str(path)
        target=source/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(get,manifest['files']))
    subprocess.run(['patch','-p1','-i',str(HERE/'runtime.patch')],cwd=source,check=True)
    for name in ('smoke.py','backend_probe.py'):shutil.copyfile(HERE/name,source/name)
    shutil.copyfile(HERE/'Dockerfile',directory/'Dockerfile')
    (directory/'output').mkdir()
    return directory


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,required=True)
    args=parser.parse_args();print(prepare(args.out_dir))
