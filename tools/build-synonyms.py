"""Build exact-primary-sense synonym data. Normal builds are entirely offline.

GPT-edited candidates are frozen locally by exact primary meaning and POS.
Never sends data to a service, merges inflections or creates vocabulary records.
"""
import argparse
import json
import hashlib
from pathlib import Path
from vocabulary_tree import entries as tree_entries
from ielts_bundles import source_decks, refresh as refresh_ielts, write as write_json

ROOT = Path(__file__).resolve().parents[1]
CURATED = ROOT / 'learning/synonyms.json'
PAYLOAD = ROOT / 'learning/synonyms.json'
EDITED = ROOT / 'tools/gpt-synonyms.tsv'
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, data):
    write_json(path, data)

def sources():
    return [ROOT / 'seed_words.json', *source_decks(ROOT)]

def key(w):
    return (w['word'].lower(), w.get('pos', ''), w['meaningVi'])

def entries(include_basic=True):
    result = {}
    phrase_names = {line.split('|')[0] for line in (ROOT/'tools/curated-prepositions.tsv').read_text(encoding='utf-8').splitlines()
                    if line and not line.startswith('#')}
    phrase_names.update(line.split('|')[0] for line in (ROOT/'tools/curated-root-phrases-500.tsv').read_text(encoding='utf-8').splitlines()
                        if line and not line.startswith('#'))
    for path in sources():
        if not include_basic and path.name in {'basic-20.json','basic-120.json','everyday-500.json','prepositions.json'}: continue
        for w in tree_entries(read(path)):
            if not include_basic and w['word'] in phrase_names: continue
            result.setdefault(key(w), {k: w.get(k, '') for k in ('word', 'pos', 'meaningVi', 'example')})
    return sorted(result.values(), key=key)

def apply():
    records = read(CURATED)
    lookup = {key(r): r for r in records}
    assert len(lookup) == len(records)
    assert set(lookup) == {key(w) for w in entries()}, 'Curation must cover every exact primary meaning'
    write(PAYLOAD, records)
    for path in sources():
        deck = read(path)
        for w in tree_entries(deck):
            w['synonyms'] = lookup[key(w)]['synonyms']
        write(path, deck)
    from phrase_bundles import refresh_offline
    refresh_offline()
    refresh_ielts(ROOT)
    print(f'Applied {len(records)} meanings; {sum(bool(r["synonyms"]) for r in records)} with synonyms, no added vocabulary rows.')

def local_build():
    words = entries(include_basic=False)
    identity_hash = hashlib.sha256(json.dumps([key(w) for w in words],
        ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()
    assert identity_hash == '4e3b5756b2cf94de07e77472527b130b90f49bdc393f5bdc05d2c3e238466383', \
        'Canonical identities changed; re-index and review GPT editing before rebuilding'
    covered, alternatives = set(), {}
    for line in EDITED.read_text(encoding='utf-8').splitlines():
        if line.startswith('# reviewed '):
            start, end = map(int, line.removeprefix('# reviewed ').split(':'))
            assert not covered.intersection(range(start, end))
            covered.update(range(start, end))
        elif line and not line.startswith('#'):
            index, values = line.split('|', 1)
            index = int(index)
            assert index not in alternatives
            alternatives[index] = values.split(';')
    assert covered == set(range(len(words))), 'GPT editing must cover every primary meaning'
    existing = ({key(w): w['synonyms'] for w in read(CURATED) if w['source'] == 'existing-editorial'}
        if CURATED.exists() else {key(w): w['synonyms'] for p in sources() for w in read(p) if w.get('synonyms')})
    records = []
    for i, w in enumerate(words):
        values = existing.get(key(w), alternatives.get(i, []))
        records.append(dict(word=w['word'], pos=w['pos'], meaningVi=w['meaningVi'], synonyms=values,
            reason='' if values else 'Chưa xác định từ đồng nghĩa phổ biến phù hợp với đúng nghĩa và từ loại này.',
            source='existing-editorial' if key(w) in existing else 'gpt-edited'))
    for name in ('basic-20.json','basic-120.json','everyday-500.json','prepositions.json'):
        supplement = ROOT / 'decks' / name
        if not supplement.exists(): continue
        for w in tree_entries(read(supplement)):
            values = w['synonyms']
            records.append(dict(word=w['word'], pos=w['pos'], meaningVi=w['meaningVi'], synonyms=values,
                reason='' if values else 'Chưa xác định từ đồng nghĩa phổ biến phù hợp với đúng nghĩa và từ loại này.',
                source='gpt-edited'))
    # Curated phrases also live in original source decks outside these supplements.
    phrase_names = {line.split('|')[0] for line in (ROOT/'tools/curated-prepositions.tsv').read_text(encoding='utf-8').splitlines()
                    if line and not line.startswith('#')}
    phrase_names.update(line.split('|')[0] for line in (ROOT/'tools/curated-root-phrases-500.tsv').read_text(encoding='utf-8').splitlines()
                        if line and not line.startswith('#'))
    for w in read(CURATED):
        if w['word'] in phrase_names:
            records.append(w)
    records = list({key(r):r for r in records}.values())
    records.sort(key=key)
    write(CURATED, records)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--local-build', action='store_true')
    args = parser.parse_args()
    if args.local_build: local_build()
    if args.apply: apply()
