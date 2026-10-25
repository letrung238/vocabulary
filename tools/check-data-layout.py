"""Validate the single public data source, catalog and derived phrase view."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from phrase_bundles import sources, refresh_offline
from vocabulary_tree import entries

ROOT = Path(__file__).resolve().parents[1]

def main():
    catalog = json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))
    urls = [row['url'] for row in catalog['files']]
    assert len(urls) == len(set(urls))
    expected = {p.resolve() for p in sources(ROOT)}
    assert expected == {(ROOT/url).resolve() for url in urls}
    words = []
    for row in catalog['files']:
        path = (ROOT/row['url']).resolve()
        assert path.is_relative_to(ROOT)
        data = json.loads(path.read_text(encoding='utf-8'))
        assert len(data) == row['count'], row['url']
        words.extend(data)
    assert len({w['word'] for w in words}) == 5520
    assert len({w['word'] for w in entries(words)}) == 6169
    assert sum(len(w.get('phrases',[])) for w in words) == 649
    view = refresh_offline(ROOT)
    assert len(view) == 189 and sum(len(w.get('phrases',[])) for w in view) == 649
    by_hash = defaultdict(list)
    for folder in ['decks','learning','tools','practice','pronunciation']:
        for path in (ROOT/folder).rglob('*'):
            if path.is_file() and path.suffix in {'.json','.tsv','.txt','.gzip'} and '__pycache__' not in path.parts:
                by_hash[hashlib.sha256(path.read_bytes()).digest()].append(path.relative_to(ROOT).as_posix())
    assert all(len(paths)==1 for paths in by_hash.values()), [paths for paths in by_hash.values() if len(paths)>1]
    assert not (ROOT/'it_advanced.json').exists()
    assert len(json.loads((ROOT/'decks/prepositions.json').read_text(encoding='utf-8'))) == 33
    print(f'PASS: single public source; {len(urls)} catalog sources, 5520 roots / 649 nested phrases; 189-parent phrase view; no byte-identical data copies.')

if __name__ == '__main__':
    main()
