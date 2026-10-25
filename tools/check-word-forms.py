"""Verify canonical counts, nested inflections and public lookup payloads."""
import argparse
import importlib.util
import json
import re
import subprocess
import sys
import hashlib
from pathlib import Path
from vocabulary_tree import entries as tree_entries
from ielts_bundles import head_records

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('word_forms', ROOT / 'tools/build-word-forms.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f'Duplicate JSON key: {key}'
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_pairs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compare-head', action='store_true')
    args = parser.parse_args()
    payload = read(builder.PAYLOAD)
    assert payload == builder.build_payload(), 'Frozen forms cannot reproduce the shipped data'
    phrase_additions = {name for names in read(ROOT/'learning/phrase-roots.json').values() for name in names} | {'care of'}
    phrase_additions |= {line.split('|')[0] for line in (ROOT/'tools/curated-phrase-roots.tsv').read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')}
    additions = {w['word'] for name in ('basic-20.json','basic-120.json','everyday-500.json') for w in read(ROOT / 'decks' / name)} | phrase_additions
    frozen = [w for w in payload if w['word'] not in additions]
    fingerprint = hashlib.sha256(json.dumps(frozen, ensure_ascii=False, sort_keys=True,
        separators=(',', ':')).encode('utf-8')).hexdigest()
    assert fingerprint == '25fd6f1bc198d0933935b9d45b12cf9e97dfb5e9acc3b28628d0fa8344cb2295', 'Previous forms changed'
    new_words={w['word'] for w in read(ROOT/'decks/everyday-500.json')} | phrase_additions
    previous=[w for w in payload if w['word'] not in new_words]
    previous_hash=hashlib.sha256(json.dumps(previous,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert previous_hash=='83f482c7ada55777beb37c641e355cb4f3cb081bd935171a460d7c732fbaea71', 'Pre-500 forms changed'
    assert len(payload) == 4188
    assert sum(len(w['forms']) for w in payload) == 8091
    assert len(builder.nouns()) == 3911
    assert sum('plural' in f['types'] for w in payload for f in w['forms']) == 2930
    verb_payload = [{**w, 'forms': [dict(f, types=[t for t in f['types'] if t != 'plural']) for f in w['forms'] if any(t != 'plural' for t in f['types'])]} for w in payload]
    assert sum(bool(w['forms']) for w in verb_payload) == 1798
    assert sum(len(w['forms']) for w in verb_payload) == 5684
    lookup = {w['word']: w['forms'] for w in payload}
    words = set()
    secondary = 0
    for path in builder.sources():
        data = read(path)
        assert len(data) == len({w['word'] for w in data}), path
        words.update(w['word'] for w in tree_entries(data))
        secondary += sum(len(w.get('senses', [])) for w in tree_entries(data)
            if path.name != 'prepositions.json' or w['word'] in phrase_additions)
        if args.compare_head and path.name not in {'basic-20.json','basic-120.json','everyday-500.json','prepositions.json'}:
            old = head_records(path, ROOT)
            stripped = [{k: v for k, v in w.items() if k not in {'forms','phrases'}} for w in data]
            old = [{k: v for k, v in w.items() if k not in {'forms','phrases'}} for w in builder.normalize_nouns(old)]
            assert old == stripped, f'Unexpected lexical data or progress changed: {path}'
        for word in tree_entries(data):
            expected = builder.applicable_forms(word, lookup.get(word['word'], []))
            assert word.get('forms', []) == expected, (path, word['word'])
    assert len(words) == 6169
    assert secondary == 3244
    verb_lemmas = set(builder.verbs())
    for word in payload:
        assert len(word['forms']) == len({f['word'] for f in word['forms']}), word
        types = {t for f in word['forms'] for t in f['types']}
        if word['word'] in verb_lemmas:
            assert {'present_third_person_singular', 'present_participle', 'gerund', 'past_simple', 'past_participle'} <= types
        for form in word['forms']:
            assert form['ipa'].startswith('/') and form['ipa'].endswith('/'), form
            assert bool(form.get('example')) == bool(form.get('exampleVi')), form
            if form.get('example'):
                assert re.search(r'(?<![a-z])' + re.escape(form['word'].lower()) + r'(?![a-z])', form['example'].lower()), form
    wound = next(f for f in lookup['wind'] if f['word'] == 'wound')
    assert wound['ipa'] == '/waʊnd/'
    assert next(f for f in lookup['greenhouse'] if f['word'] == 'greenhouses')['ipa'].endswith('haʊzɪz/')
    assert next(f for f in lookup['data warehouse'] if f['word'] == 'data warehouses')['ipa'].endswith('haʊzɪz/')
    paired = sum(bool(f.get('example')) for w in payload for f in w['forms'])
    assert 'bacteria' not in words and 'bacterium' in words
    plural = lambda base: {f['word'] for f in lookup.get(base, []) if 'plural' in f['types']}
    for base, expected in {'criterion': {'criteria'}, 'bacterium': {'bacteria'}, 'analysis': {'analyses'},
        'board of directors': {'boards of directors'}, 'conflict of interest': {'conflicts of interest'},
        'software bill of materials': {'software bills of materials'}, 'system on a chip': {'systems on a chip'},
        'series': {'series'}, 'headquarters': {'headquarters'}}.items():
        assert plural(base) == expected, (base, plural(base))
    for base in ['data','information','advice','equipment','software','furniture','customs','arms',
                 'leftovers','minutes','saving','graphics','integrated graphics','lessons learned',
                 'ethics','refuse','hail','cocoa']:
        assert not plural(base), (base, plural(base))
    print(f'PASS: 6169 lexical items including nested phrases / 3244 original secondary meanings; 3911 noun entries, 2930 plural forms; 1798 verb lemmas / 5684 verb forms; all previous forms preserved; {paired} bilingual contexts; public payload and frozen rebuild match.')


if __name__ == '__main__':
    main()
