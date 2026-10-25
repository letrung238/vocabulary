"""Check complete synonym curation, unchanged vocabulary and exact identities."""
import importlib.util
import json
import subprocess
import sys
import runpy
from pathlib import Path
from vocabulary_tree import entries as tree_entries
from ielts_bundles import head_records

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('synonyms_builder', ROOT / 'tools/build-synonyms.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
read = builder.read
key = builder.key

def main():
    rows = read(builder.CURATED)
    lookup = {key(r): r for r in rows}
    assert len(rows) == len(lookup) == 6178
    assert set(lookup) == {key(w) for w in builder.entries()}
    assert read(builder.PAYLOAD) == rows
    for row in rows:
        values = row['synonyms']
        assert isinstance(values, list) and len(values) <= 4
        assert len(values) == len({v.lower() for v in values})
        assert all(v.strip() == v and v and v.lower() != row['word'].lower() for v in values)
        assert (bool(values) and row['reason'] == '') or (not values and row['reason'].strip())
        assert row['source'] in ('existing-editorial', 'gpt-edited')
    all_words = set()
    for path in builder.sources():
        data = read(path)
        relative = path.relative_to(ROOT).as_posix()
        if path.name in {'basic-20.json','basic-120.json','everyday-500.json','prepositions.json'}:
            source_builder = runpy.run_path(str(ROOT/'tools'/('build-'+path.stem+'.py')))
            source = source_builder['build']()
            if path.name == 'prepositions.json':
                expected = {w['word']:w for w in source}
                actual = {w['word']:w for p in builder.sources() for w in tree_entries(read(p)) if w['word'] in expected}
                assert {name:{k:v for k,v in w.items() if k != 'forms'} for name,w in actual.items()} == expected
            else:
                assert [{k:v for k,v in w.items() if k not in {'forms','phrases'}} for w in data] == source
            baseline = data
        else:
            baseline = head_records(path, ROOT)
        # Root lexical fields/order remain unchanged; child ownership is checked separately.
        stripped = lambda entries: [{k: v for k, v in w.items() if k not in {'synonyms','phrases'}} for w in entries]
        assert stripped(data) == stripped(baseline), f'Vocabulary content/count changed: {relative}'
        all_words.update(w['word'] for w in tree_entries(data))
        for w in tree_entries(data): assert w['synonyms'] == lookup[key(w)]['synonyms']
        for old, new in zip(baseline, data):
            if old.get('synonyms'): assert old['synonyms'] == new['synonyms'], 'Existing editorial list replaced'
    assert len(all_words) == 6169
    print(f'PASS: 6169 lexical items including nested phrases / 6178 exact primary meanings; {sum(bool(r["synonyms"]) for r in rows)} lists; existing vocabulary preserved; public source identities match.')

if __name__ == '__main__': main()
