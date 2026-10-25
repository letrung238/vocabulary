"""Package an ipa-dict en_US.txt download into the shared offline asset."""
import argparse
import gzip
import hashlib
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('source', type=Path)
args = parser.parse_args()
entries = {}
for line in args.source.read_text(encoding='utf-8').splitlines():
    word, ipa = line.split('\t', 1)
    entries[word.lower().replace('’', "'")] = ipa
payload = ''.join(f'{word}\t{ipa}\n' for word, ipa in sorted(entries.items())).encode('utf-8')
target = Path(__file__).resolve().parent.parent / 'pronunciation/en-us.tsv.gzip'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))
print(f'{len(entries)} entries; {target.stat().st_size} bytes compressed')
print(f'Source SHA256: {hashlib.sha256(args.source.read_bytes()).hexdigest()}')
