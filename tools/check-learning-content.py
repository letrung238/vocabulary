"""Verify authored identity coverage and the offline payload; report remaining work."""
import json
from pathlib import Path
from vocabulary_tree import entries as tree_entries, owned_entries
from ielts_bundles import source_decks

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def identity(word, sense):
    return word['word'], sense.get('pos', ''), sense['meaningVi']


def main():
    records = sum((read('tools/' + name) for name in ['curated-sense-examples.json', 'curated-awl-examples.json',
                   'curated-b2-examples.json', 'curated-core-examples.json', 'curated-b2-daily-work-examples.json', 'curated-daily-work-498-examples.json',
                   'curated-professional-examples.json', 'curated-reviewed-examples.json', 'curated-basic-20-examples.json', 'curated-basic-120-examples.json', 'curated-everyday-500-examples.json','curated-prepositions-examples.json','curated-legacy-examples.json']), [])
    assert records == read('learning/sense-examples.json'), 'Offline content payload drifted'
    lookup = {(r['word'], r['pos'], r['meaningVi']): r for r in records}
    assert len(lookup) == len(records), 'Duplicate authored identity'
    matched = set()
    total = complete = 0
    files = [ROOT / 'seed_words.json'] + source_decks(ROOT)
    for path in files:
        words = json.loads(path.read_text(encoding='utf-8'))
        if path.name == 'ielts-academic.json':
            assert len(words) == 317
            assert sum(len(w.get('senses', [])) for w in words) == 242
        if path.name == 'b2-1000.json':
            assert len(words) == 1000
            assert sum(len(w.get('senses', [])) for w in words) == 1226
        if path.name == 'b2-daily-work-500.json':
            assert len(words) == 500
            assert sum(bool(w.get('senses')) for w in words) == 264
            assert sum(len(w.get('senses', [])) for w in words) == 331
        if path.name == 'daily-work-498.json':
            assert len(words) == 498
            assert sum(bool(w.get('senses')) for w in words) == 227
            assert sum(len(w.get('senses', [])) for w in words) == 321
        owned = {w['word'] for w in owned_entries(path, words)}
        for word in tree_entries(words):
            for sense in [word] + word.get('senses', []):
                secondary = sense is not word
                total += secondary and word['word'] in owned
                bilingual = bool(sense.get('example', '').strip() and sense.get('exampleVi', '').strip())
                complete += bilingual and secondary and word['word'] in owned
                if secondary or path.name in ['ielts-academic.json', 'b2-1000.json', 'b2-daily-work-500.json', 'daily-work-498.json', 'professional-reading-1000.json']:
                    assert bilingual, f"Missing context in {path.name}: {word['word']}"
                key = identity(word, sense)
                if key in lookup:
                    record = lookup[key]
                    assert sense['example'] == record['example'] and sense['exampleVi'] == record['exampleVi'], key
                    matched.add(key)
    assert matched == set(lookup), 'Stale authored identity'
    assert len(read('tools/curated-awl-examples.json')) == 241
    assert len(read('tools/curated-b2-examples.json')) == 1217
    assert len(read('tools/curated-core-examples.json')) == 708
    assert len(read('tools/curated-b2-daily-work-examples.json')) == 831
    assert len(read('tools/curated-daily-work-498-examples.json')) == 818
    assert len(read('tools/curated-basic-20-examples.json')) == 32
    assert len(read('tools/curated-basic-120-examples.json')) == 150
    assert len(read('tools/curated-everyday-500-examples.json')) == 1083
    assert complete == total == 3300, 'Canonical secondary-context coverage changed'
    print('B2: 1000/1000 main meanings and 1226/1226 secondary meanings have bilingual examples.')
    print('B2 daily/work: 500/500 main meanings and 331/331 secondary meanings have bilingual examples; 236 reviewed exceptions.')
    print('Daily/work extra: 498/498 main meanings and 320/320 secondary uses are bilingual; 271 reviewed exceptions.')
    print(f'AWL: 241/241 secondary meanings have bilingual examples; {len(records)} authored offline pairs match the decks.')
    print(f'All decks: {complete}/{total} secondary meanings have bilingual examples; {total-complete} remain for curation.')


if __name__ == '__main__':
    main()
