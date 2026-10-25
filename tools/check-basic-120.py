"""Verify the exact 120 approved additions, linguistic edge cases and catalog."""
import json
import re
import runpy
import sys
from pathlib import Path
from vocabulary_tree import owned_entries

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
norm=lambda w:re.sub(r'[\s\-‐‑‒–—]+',' ',w.strip().lower())
source=runpy.run_path(str(ROOT/'tools/build-basic-120.py'))['build']()
approved=[
'know|think|ask|tell|find|give|want|need|use|try|leave|buy|sell|pay|read|write|speak|listen|help|work',
'kettle|saucepan|drawer|toothpaste|toothbrush|shampoo|soap|towel|sink|sponge|detergent|dishwasher|washing machine|freezer|vacuum cleaner|broom|mop|shelf|cupboard|curtain',
'bread|rice|pasta|potato|tomato|onion|garlic|carrot|lettuce|cucumber|beef|pork|chicken|fish|egg|cheese|butter|yogurt|milk|flour',
'shirt|sweater|jacket|coat|jeans|shorts|skirt|dress|sock|shoe|boot|hat|scarf|glove|belt|underwear|pajamas|swimsuit|zipper|pocket',
'head|face|eye|ear|nose|mouth|tooth|neck|shoulder|arm|hand|finger|stomach|leg|knee|foot|brain|headache|bandage|painkiller',
'bus stop|train station|timetable|boarding pass|departure gate|baggage claim|seat belt|traffic light|crosswalk|roundabout|parking lot|parking meter|speed limit|traffic jam|detour|shortcut|suitcase|backpack|umbrella|travel adapter']
expected=[w for group in approved for w in group.split('|')]
deck=read(ROOT/'decks/basic-120.json')
assert [w['word'] for w in deck]==expected
assert len(deck)==len(set(map(norm,expected)))==120
assert [{k:v for k,v in w.items() if k not in {'forms','phrases'}} for w in deck]==source
prior=[w for p in [ROOT/'seed_words.json',*sorted((ROOT/'decks').glob('*.json'))] if p.name!='basic-120.json' for w in owned_entries(p, read(p))]
known={norm(w['word']) for w in prior}|{norm(f['word']) for w in prior for f in w.get('forms',[])}
assert not known&set(map(norm,expected)), 'Existing vocabulary or inflection duplicated'
assert len({w['word'] for w in prior})==6666-sum(len(w.get('phrases',[])) for w in deck)
by_word={w['word']:w for w in deck}
forms=lambda word:{f['word'] for f in by_word[word].get('forms',[])}
assert forms('tooth')=={'teeth'} and forms('foot')=={'feet'}
assert forms('shelf')=={'shelves'} and forms('scarf')=={'scarves','scarfs'}
assert {'read','reading','reads'}==forms('read')
assert next(f['ipa'] for f in by_word['read']['forms'] if f['word']=='read')=='/red/'
for word in ('rice','milk','underwear','jeans','shorts','pajamas','bread','soap','toothpaste','garlic','lettuce','baggage claim'):
    assert not forms(word), f'Spurious inflection: {word}'
assert next(f['ipa'] for f in by_word['mouth']['forms'] if f['word']=='mouths')=='/maʊðz/'
uses=next(f for f in by_word['use']['forms'] if f['word']=='uses')
assert set(uses['types'])=={'plural','present_third_person_singular'}
assert set(uses['ipa'].split(', '))=={'/juːzɪz/','/juːsɪz/'}
assert {'wrote','written'}<=forms('write') and 'bought' in forms('buy')
assert forms('bus stop')=={'bus stops'} and forms('boarding pass')=={'boarding passes'}
examples=[s for w in deck for s in [w]+w.get('senses',[])]
assert len(examples)==150 and all(s['example'] and s['exampleVi'] for s in examples)
listings=[[f for f in read(ROOT/p)['files'] if f['url']=='decks/basic-120.json'] for p in ('catalog.json',)]
assert len(listings[0])==1 and listings[0][0]['count']==120
print('PASS: exactly 120 approved new roots, 150 bilingual contexts, irregular forms/IPA, mass and plural-only nouns, no duplicates, catalog and public source.')
