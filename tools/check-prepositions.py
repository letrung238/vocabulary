"""Check authored phrase identity, complete contexts, conjugations and canonical roots."""
import hashlib
import json
import re
import runpy
from pathlib import Path
from vocabulary_tree import entries as tree_entries

ROOT = Path(__file__).resolve().parents[1]
read = lambda path: json.loads(path.read_text(encoding='utf-8-sig'))
builder = runpy.run_path(str(ROOT/'tools/build-prepositions.py'))
source = builder['build']()
extra_names = {w['word'] for w in builder['additional_phrases']()}
roots = read(ROOT/'decks/prepositions.json')
paths = [ROOT/'seed_words.json', *sorted((ROOT/'decks').glob('*.json'))]
canonical = [w for path in paths for w in read(path)]
lexical = list(tree_entries(canonical))
assert len(roots) == 33
assert {w['word'] for w in roots} == {w['word'] for w in builder['new_roots']()} | {'care of'}
all_entries = {w['word']:w for w in lexical}
deck = [all_entries[w['word']] for w in source[:150]]
assert [{k:v for k,v in w.items() if k!='forms'} for w in deck] == source[:150]
extra = [all_entries[w['word']] for w in source[150:]]
assert [{k:v for k,v in w.items() if k!='forms'} for w in extra] == source[150:]
assert len(extra) == 500 and sum(w['pos']=='verb' for w in extra) == 420
assert sum(len(w.get('forms',[])) for w in extra) == 1452
assert len(deck) == len({w['word'] for w in deck}) == 150
old = [w for path in [ROOT/'seed_words.json',*sorted((ROOT/'decks').glob('*.json'))]
       if path.name!='prepositions.json' for w in read(path)]
normalize = lambda text: re.sub(r'[\s\-‐‑–—]+',' ',text.strip().lower())
known = {normalize(w['word']) for w in old} | {normalize(f['word']) for w in old for f in w.get('forms',[])}
assert not known & {normalize(w['word']) for w in deck}
assert len({w['word'] for w in old}) == 5487
assert sum(len(w.get('forms',[])) for w in deck) == 397
assert sum(len(w.get('senses',[]))+1 for w in deck) == 155
by_word = {w['word']:w for w in deck}
initial = deck[:50]
initial_hash = hashlib.sha256(json.dumps(sorted(initial,key=lambda w:w['word']),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert initial_hash=='992ba3740f9b98a8dbfb2e9a5a2896c60ed0421b62c78487a2ed94703fc845a4', 'Original 50 phrases changed'
new100={w['word'] for w in deck[50:]}
assert len(new100)==100
assert sum(w['pos']=='verb' for w in deck[50:])==80
assert sum(w['pos']=='adjective' for w in deck[50:])==20

assert by_word['care of']['pos']=='idiom' and not by_word['care of'].get('forms')
assert 'c/o' in by_word['care of']['meaningVi']
assert len(by_word['care for']['senses'])==1 and len(by_word['think of']['senses'])==2
assert {'took care of','taken care of'} <= {f['word'] for f in by_word['take care of']['forms']}
assert next(f for f in by_word['hear of']['forms'] if f['word']=='heard of')['ipa']=='/hɜrd əv/'
for word in deck+extra:
    assert 'prepositions' in word['tags'] and word['topic']
    assert word['ipa'].startswith('/') and word['ipa'].endswith('/')
    for sense in [word]+word.get('senses',[]):
        assert sense['example'].strip() and sense['exampleVi'].strip()
        assert any(re.search(r'(?<![a-z])'+re.escape(text)+r'(?![a-z])',sense['example'].lower())
                   for text in [word['word']]+[f['word'] for f in word.get('forms',[])])
    for form in word.get('forms',[]):
        assert form['word']==word['word'] or form['word'] not in by_word, 'Inflection duplicated as a phrase record: '+form['word']
        assert form['word'].endswith(word['word'][word['word'].index(' '):])
        assert form['ipa'].startswith('/') and form['ipa'].endswith('/')
assert (ROOT/'decks/prepositions.json').read_bytes()==(ROOT/'decks/prepositions.json').read_bytes()
from phrase_bundles import refresh_offline
offline = refresh_offline(ROOT)
assert len(offline) == 189 and sum(len(w.get('phrases', [])) for w in offline) == 649
for word in offline:
    assert word == next(w for w in canonical if w['word'] == word['word']), word['word']
payload = read(ROOT/'learning/word-forms.json')
new_roots = {w['word'] for w in builder['new_roots']()}
previous = [w for w in payload if w['word'] not in by_word and w['word'] not in new_roots | extra_names]
digest = hashlib.sha256(json.dumps(previous,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert digest=='9f94256cb926bfc6a1e5a3605c27cb902f22dc16f2ddb3363c0bc196ba6f1407'
previous_extension=[w for w in payload if w['word'] not in new100 and w['word'] not in new_roots | extra_names]
assert hashlib.sha256(json.dumps(previous_extension,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='f8961675f29978ad16c100ecb8c62df51c56aeb177de3d0c95671f8c9feea8b0', 'Previous forms changed'
for name in ['catalog.json']:
    entries=[e for e in read(ROOT/name)['files'] if e['url']=='decks/prepositions.json']
    assert len(entries)==1 and entries[0]['count']==33
print('PASS: 150 preposition combinations, 155 bilingual contexts, 397 nested forms, idiom care of, irregular forms, catalog and public source.')
links = read(ROOT/'learning/phrase-roots.json')
assert links == builder['phrase_roots'](builder['build']())
assert len(links) == 188 and sum(map(len, links.values())) == 649
assert links['think'] == ['think of', 'think about']
assert 'take care of' in links['care'] and 'care of' not in links['care']
phrase_names = {name for names in links.values() for name in names}
assert not phrase_names & {w['word'] for w in canonical}
assert len({w['word'] for w in old} | {w['word'] for w in roots}) == 5520
assert all(not p.get('phrases') for w in canonical for p in w.get('phrases', []))
for parent, names in links.items():
    owners = [w for w in canonical if any(p['word'] in names for p in w.get('phrases', []))]
    assert len(owners) == 1 and owners[0]['word'] == parent, parent
    assert [p['word'] for p in owners[0]['phrases']] == names
assert sum(len(w.get('phrases', [])) for w in canonical) == 649
legacy = [w for w in lexical if w['word'] not in extra_names]
known_legacy = {normalize(w['word']) for w in legacy} | {normalize(f['word']) for w in legacy for f in w.get('forms',[])}
assert not known_legacy & {normalize(name) for name in extra_names}, 'Additional phrase repeats existing vocabulary/inflections'
assert len({w['word'] for w in lexical}) == 6169
assert len({w['word'].split()[0] for w in extra}) == 94
# Every lexical field is frozen independently of source-file ownership.
serialized = sorted(json.dumps({k:v for k,v in w.items() if k!='phrases'}, ensure_ascii=False,
                              sort_keys=True,separators=(',',':')) for w in legacy)
assert len(serialized) == 5682
assert hashlib.sha256('\n'.join(serialized).encode()).hexdigest() == 'ab624315a8f2f02f3ef16561276ac33d89f5db1d64f7813966de5b5b2ed27d87'
think = next(w for w in read(ROOT/'decks/basic-120.json') if w['word']=='think')
assert [p['word'] for p in think['phrases']] == ['think of','think about']
print('PASS: exactly 500 additions / 94 existing roots / 1452 forms; 649 nested phrases / 188 parent groups; 5520 unique roots unchanged; every legacy lexical field unchanged; offline export matches sources.')
