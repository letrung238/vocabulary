"""Verify only the 20 approved vocabulary additions and their authored content."""
import json
import runpy
import sys
from pathlib import Path
from vocabulary_tree import owned_entries

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
source = runpy.run_path(str(ROOT/'tools/build-basic-20.py'))['build']()
approved = {'book','pass','get','take','make','keep','bring','choose','remember','forget',
    'wallet','receipt','refund','charger','luggage','pharmacy','follow up','figure out','put off','run out of'}
deck = read(ROOT/'decks/basic-20.json')
assert len(deck) == len({w['word'] for w in deck}) == 20
assert {w['word'] for w in deck} == approved
assert [{k:v for k,v in w.items() if k not in {'forms','phrases'}} for w in deck] == source
old = {w['word'] for p in [ROOT/'seed_words.json', *sorted((ROOT/'decks').glob('*.json'))]
       if p.name!='basic-20.json' for w in owned_entries(p, read(p))}
assert not old.intersection(approved), 'Addition duplicates existing root'
assert len(old)==6648-sum(len(w.get('phrases',[])) for w in deck)
normalize = lambda word: word.replace('-', ' ').lower()
assert {normalize(w) for w in old}&{normalize(w) for w in approved} == {'follow up'}
by_word = {w['word']:w for w in deck}
assert len(by_word['book']['senses'])==1 and by_word['book']['senses'][0]['pos']=='verb'
assert any(f['word']=='books' and {'plural','present_third_person_singular'} <= set(f['types'])
           for f in by_word['book']['forms'])
assert not by_word['luggage'].get('forms'), 'Uncountable luggage acquired a plural'
assert any(f['word']=='taken' and 'past_participle' in f['types'] for f in by_word['take']['forms'])
assert any(f['word']=='ran out of' and 'past_simple' in f['types'] for f in by_word['run out of']['forms'])
examples = [s for w in deck for s in [w]+w.get('senses',[])]
assert len(examples)==32 and all(s['example'] and s['exampleVi'] for s in examples)
listing = [f for f in read(ROOT/'catalog.json')['files'] if f['url']=='decks/basic-20.json']
assert len(listing)==1 and listing[0]['count']==20
assert [f for f in read(ROOT/'catalog.json')['files'] if f['url']=='decks/basic-20.json'] == listing
print('PASS: exactly 20 approved entries (19 new roots, follow up shares follow-up), 32 bilingual examples, book/books, irregular and phrasal forms, mass luggage, public source and catalog.')
