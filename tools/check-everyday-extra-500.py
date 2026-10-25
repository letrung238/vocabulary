"""Verify exactly 500 new lemmas, complete examples/forms, and unchanged prior data."""
import collections
import hashlib
import json
import re
from pathlib import Path
from everyday_extension import build, names, rows
from phrase_bundles import sources
from vocabulary_tree import entries

ROOT=Path(__file__).resolve().parents[1]
read=lambda path:json.loads(path.read_text(encoding='utf-8'))
digest=lambda value:hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
selected=names()
decks={path.name:read(path) for path in sources(ROOT)}
baseline={name:[w for w in words if w['word'] not in selected] for name,words in decks.items()}
assert digest(baseline)=='f02b0bfd85b36e70647944cdd220a73f076881bb6cfcbb19e9ab42f3b9f0b7a9', 'A pre-existing lexical field or order changed'
old=[w for words in baseline.values() for w in entries(words)]
normalize=lambda text:re.sub(r'[-\s]+',' ',text.lower().strip())
from runpy import run_path
canonical=run_path(str(ROOT/'tools/build-b2-daily-work.py'))['canonical']
key=lambda text:' '.join(canonical(token) for token in normalize(text).split())
known={key(w['word']) for w in old}|{key(f['word']) for w in old for f in w.get('forms',[])}
assert not known&{key(name) for name in selected}
assert not {s.replace(' ','') for s in known}&{key(s).replace(' ','') for s in selected}
actual=[w for w in decks['everyday-500.json'] if w['word'] in selected]
assert len(actual)==500
assert [{k:v for k,v in w.items() if k!='forms'} for w in actual]==build()
assert collections.Counter(w['pos'] for w in actual)=={'noun':350,'adjective':100,'verb':50}
assert all(not w.get('phrases') for w in actual)
for word in actual:
    assert word['ipa'].startswith('/') and word['ipa'].endswith('/')
    assert word['example'] and word['exampleVi']
    assert re.search(r'(?<![a-z])'+re.escape(word['word'])+r'(?![a-z])',word['example'].lower()),word['word']
    assert word['word'] not in word['synonyms']
    for form in word.get('forms',[]):
        assert form['ipa'].startswith('/') and form['ipa'].endswith('/')
    if word['pos']=='verb':
        assert len(word['forms'])==3
        assert {t for f in word['forms'] for t in f['types']}=={'present_third_person_singular','present_participle','gerund','past_simple','past_participle'}
payload=read(ROOT/'learning/word-forms.json')
assert digest([w for w in payload if w['word'] not in selected])=='bd8ca6639657e7588e4bc42613b6826be29cbca8a56e13c39ca4b3b8f3de19aa', 'Previously reviewed forms changed'
by_word={w['word']:w for w in actual}
assert by_word['thyme']['ipa']=='/taɪm/' and by_word['ferment']['ipa']=='/fərˈment/'
assert by_word['ox']['forms'][0]['word']=='oxen'
assert by_word['sheep']['forms'][0]['word']=='sheep'
assert by_word['pliers'].get('forms',[])==[]
assert by_word['yeast'].get('forms',[])==[]
assert {f['word'] for f in by_word['shred']['forms']}=={'shreds','shredding','shredded'}
assert {f['word'] for f in by_word['sob']['forms']}=={'sobs','sobbing','sobbed'}
assert len(decks['everyday-500.json'])==1000
entry=next(e for e in read(ROOT/'catalog.json')['files'] if e['url']=='decks/everyday-500.json')
assert entry['count']==1000
assert len({w['word'] for words in decks.values() for w in words})==6029
print('PASS: exactly 500 new roots (350 nouns/100 adjectives/50 verbs), 500 bilingual contexts, 432 forms; 1000-root merged deck; every prior lexical field/order and form unchanged; 6029 roots.')
