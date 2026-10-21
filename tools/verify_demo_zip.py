"""Verify downloaded player ZIP against its separately retained package receipt."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import zipfile
try:
    from .release_common import file_hash
    from .build_public_demo import ROM
except ImportError:
    from release_common import file_hash
    from build_public_demo import ROM


def verify(archive, receipt, destination):
    archive,receipt,destination=map(Path,(archive,receipt,destination));r=json.loads(receipt.read_text())
    if file_hash(archive)!=r['archive_sha256']:raise ValueError('Archive checksum mismatch')
    with zipfile.ZipFile(archive)as z:
        names=z.namelist()
        if len(names)!=len(set(names))or set(names)!=set(r['payload_sha256']):raise ValueError('ZIP inventory mismatch')
        payload={}
        for n in names:
            p=PurePosixPath(n)
            if p.is_absolute()or '..'in p.parts or '\\'in n:raise ValueError('Unsafe ZIP path')
            data=z.read(n)
            if hashlib.sha256(data).hexdigest()!=r['payload_sha256'][n]:raise ValueError('ZIP member checksum mismatch')
            payload[n]=data
    if hashlib.sha256(payload[ROM]).hexdigest()!=r['rom_sha256']:raise ValueError('ROM mismatch')
    destination.mkdir(parents=True,exist_ok=False)
    for n,data in payload.items():
        p=destination/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    return dict(archive_sha256=file_hash(archive),rom_sha256=file_hash(destination/ROM),members=len(payload),extraction='passed')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('archive',type=Path);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--extract-to',type=Path,required=True);a=p.parse_args();print(json.dumps(verify(a.archive,a.receipt,a.extract_to),indent=2))
