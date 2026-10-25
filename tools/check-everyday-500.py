"""Verify approved identities, full bilingual coverage and linguistic edge cases."""
import hashlib
import json
import re
import runpy
import sys
from pathlib import Path
from vocabulary_tree import owned_entries

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
builder=runpy.run_path(str(ROOT/'tools/build-everyday-500.py'))
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
norm=lambda w:re.sub(r'[\s\-‐‑‒–—]+',' ',w.strip().lower())
from everyday_extension import names as extension_names
full=read(ROOT/'decks/everyday-500.json')
assert len(full)==1000
deck=[word for word in full if word['word'] not in extension_names()]
proposal=builder['proposed']()
assert len(deck)==len({norm(w['word']) for w in deck})==500
assert [w['word'] for w in deck]==[w for _,w,_ in proposal]
assert [{k:v for k,v in w.items() if k not in {'forms','phrases'}} for w in deck]==builder['build']()[:500]
old=[w for path in [ROOT/'seed_words.json',*sorted((ROOT/'decks').glob('*.json'))] if path.name!='everyday-500.json' for w in owned_entries(path, read(path))]
known={norm(w['word']) for w in old}|{norm(f['word']) for w in old for f in w.get('forms',[])}
assert not {norm(w['word']) for w in deck}&known
assert not {norm(w['word']).replace(' ','') for w in deck}&{w.replace(' ','') for w in known}
assert len({w['word'] for w in old})==5786-sum(len(w.get('phrases',[])) for w in deck)
assert sum(len(w.get('forms',[])) for w in deck)==528
examples=[s for w in deck for s in [w]+w.get('senses',[])]
assert len(examples)==583 and all(s['example'].strip() and s['exampleVi'].strip() for s in examples)
by_word={w['word']:w for w in deck}
surface=lambda word:{f['word'] for f in by_word[word].get('forms',[])}
for base,plural in {'child':'children','grandchild':'grandchildren','wife':'wives','calf':'calves','mother-in-law':'mothers-in-law',
    'father-in-law':'fathers-in-law','son-in-law':'sons-in-law','daughter-in-law':'daughters-in-law',
    'brother-in-law':'brothers-in-law','sister-in-law':'sisters-in-law','half-brother':'half-brothers'}.items():
    assert surface(base)=={plural},base
for word in builder['LEXICAL_PLURAL']:
    assert not surface(word),f'Plural-only noun acquired a fabricated form: {word}'
for word in ('housework','cotton','wool','postage','bacon','rice','ride-sharing','diarrhea','constipation'):
    if word in by_word: assert not surface(word),word
assert {'went','gone'}<=surface('go') and {'drove','driven'}<=surface('drive')
assert {'ate','eaten'}<=surface('eat') and {'rang','rung'}<=surface('ring')
assert surface('swelling') == {'swellings'}
assert by_word['windy']['ipa']=='/ˈwɪndi/'
assert by_word['overpriced']['ipa']=='/ˌoʊvərˈpraɪst/'
assert by_word['emergency room']['ipa']=='/ɪˈmɜrdʒənsi ˈruːm/'
assert 'mʌðər' in by_word['great-grandmother']['ipa']
assert 'ˌkærəˈsel' in by_word['baggage carousel']['ipa']
assert next(f for f in by_word['hear']['forms'] if f['word']=='heard')['ipa']=='/hɜrd/'
assert 'bàn để là quần áo' in by_word['ironing board']['exampleVi']
assert by_word['live']['ipa']=='/lɪv/'
assert any(s['pos']=='adjective' and s['ipa']=='/laɪv/' for s in by_word['live']['senses'])
assert by_word['update']['ipa']=='/ˈʌpdeɪt/'
assert any(s['pos']=='verb' and s['ipa']=='/ʌpˈdeɪt/' for s in by_word['update']['senses'])
for word in deck:
    assert word['ipa'].startswith('/') and word['ipa'].endswith('/')
    assert len(word['synonyms'])==len(set(word['synonyms']))
    for sense in [word]+word.get('senses',[]):
        patterns=[word['word']]+[f['word'] for f in word.get('forms',[])]
        assert any(re.search(r'(?<![a-z])'+re.escape(p.lower())+r'(?![a-z])',sense['example'].lower()) for p in patterns),(word['word'],sense['example'])
listings=[[f for f in read(ROOT/p)['files'] if f['url']=='decks/everyday-500.json'] for p in ['catalog.json']]
assert len(listings[0])==1 and listings[0][0]['count']==1000
print('PASS: exactly 500 approved roots, 583 bilingual meanings, 528 nested forms, no prior duplicates, mass/plural-only nouns, irregular plurals, homograph IPA, catalog and public source.')
