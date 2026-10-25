"""Build the 500-word supplement only from reviewed, versioned local sources."""
import json
import re
from pathlib import Path
from vocabulary_tree import owned_entries

ROOT = Path(__file__).resolve().parents[1]
DECK = 'decks/b2-daily-work-500.json'
VARIANTS = dict(honour='honor', mould='mold', colour='color', colourful='colorful',
                centre='center', theatre='theater', programme='program', organise='organize',
                analyse='analyze', offence='offense', defence='defense', licence='license',
                grey='gray', catalogue='catalog', travelling='traveling', speciality='specialty',
                enquiry='inquiry', litre='liter', globalisation='globalization',
                humour='humor', organisation='organization', organiser='organizer',
                adviser='advisor', modernisation='modernization', neighbourhood='neighborhood',
                authorise='authorize', unauthorised='unauthorized', minimise='minimize',
                characterise='characterize', enquire='inquire', favourable='favorable',
                jewellery='jewelry')
POS = {'noun': 'n.', 'verb': 'v.', 'adjective': 'adj.', 'adverb': 'adv.',
       'preposition': 'prep.', 'conjunction': 'conj.'}


def read(file):
    return json.loads((ROOT / file).read_text(encoding='utf-8'))


def write(file, data):
    # Preserve nested inflections when regenerating vocabulary decks.
    forms_path = ROOT / 'learning/word-forms.json'
    if forms_path.exists() and (file.startswith(('decks/',)) or file.endswith('seed_words.json')) and isinstance(data, list):
        forms = {w['word']: w['forms'] for w in json.loads(forms_path.read_text(encoding='utf-8'))}
        for word in data:
            if word.get('word') in forms:
                positions = {s.get('pos') for s in [word] + word.get('senses', [])}
                selected = [dict(f, types=[t for t in f['types'] if ('noun' if t == 'plural' else 'verb') in positions]) for f in forms[word['word']]]
                selected = [f for f in selected if f['types']]
                if len(positions & {'noun','verb'}) == 1:
                    combined = {f['word'] for f in forms[word['word']] if 'plural' in f['types'] and any(t != 'plural' for t in f['types'])}
                    for f in selected:
                        if f['word'] in combined:
                            readings = re.findall(r'/[^/]+/', f['ipa'])
                            f['ipa'] = readings[-1] if 'noun' in positions else readings[0]
                if 'verb' not in positions:
                    combined = {f['word'] for f in forms[word['word']] if any(t != 'plural' for t in f['types'])}
                    for f in selected:
                        if f['word'] in combined:
                            f.pop('example', None); f.pop('exampleVi', None)
                if selected:
                    word['forms'] = selected
    target = ROOT / file
    if isinstance(data, list):
        from phrase_bundles import retain_children
        retain_children(target, data)
    target.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if not target.exists() or target.read_bytes() != content:
        target.write_bytes(content)


def rows(file):
    return [line.split('|') for line in (ROOT / 'tools' / file).read_text(encoding='utf-8').splitlines()
            if line and not line.startswith('#')]


def canonical(word):
    word = word.strip().casefold()
    return VARIANTS.get(word, word)


def main():
    primary = rows('curated-b2-daily-work-primary.tsv')
    secondary = rows('curated-b2-daily-work-secondary.tsv')
    provenance = read('tools/b2-daily-work-provenance.json')
    evidence = {r['word']: r for r in provenance}
    assert len(primary) == len(evidence) == len(provenance) == 500
    assert set(evidence) == {r[0] for r in primary}, 'Provenance drifted from the curated selection'
    files = [ROOT / 'seed_words.json'] + sorted((ROOT / 'decks').glob('*.json'))
    existing = {canonical(w['word']) for f in files if f.name != Path(DECK).name
                for w in owned_entries(f, json.loads(f.read_text(encoding='utf-8')))}
    words = {}
    seen = set()
    for row in primary:
        assert len(row) == 6, row
        word, pos, meaning, example, translation, topic = row
        key = canonical(word)
        assert key not in existing and key not in seen, f'Duplicate word/spelling variant: {word}'
        assert re.fullmatch(r'[a-z]+(?:-[a-z]+)?', word), word
        assert all(s.strip() for s in row), word
        record = evidence[word]
        assert record['ipaReviewed'] and record['ipa'].startswith('/') and record['ipa'].endswith('/'), word
        # Match the primary part of speech; a model label for another POS is insufficient.
        assert any(e['level'] == 'B2' and (POS[pos] in e.get('entry', '') or
                   pos in e.get('pos', []) or e.get('pos') == pos)
                   for e in record['levelEvidence']), f'No B2 evidence for {word} ({pos})'
        words[word] = dict(word=word, ipa=record['ipa'], pos=pos, meaningVi=meaning,
                           example=example, exampleVi=translation, level='B2', topic=topic,
                           tags=['b2', 'b2-daily-work', topic])
        seen.add(key)
    for row in secondary:
        assert len(row) in (5, 6) and all(s.strip() for s in row), row
        word, pos, meaning, example, translation = row[:5]
        target = words[word]
        assert pos in POS
        sense = dict(pos=pos, meaningVi=meaning, example=example, exampleVi=translation,
                     ipa=row[5] if len(row) == 6 else target['ipa'])
        identities = {(s['pos'], s['meaningVi']) for s in [target] + target.get('senses', [])}
        assert (pos, meaning) not in identities and meaning != target['meaningVi'], word
        target.setdefault('senses', []).append(sense)
    deck = list(words.values())
    write(DECK, deck)
    pairs = [dict(word=w['word'], sourceGroup='b2-daily-work', **{k: s[k]
             for k in ['pos', 'meaningVi', 'example', 'exampleVi']})
             for w in deck for s in [w] + w.get('senses', [])]
    write('tools/curated-b2-daily-work-examples.json', pairs)
    multi = sum(bool(w.get('senses')) for w in deck)
    for file in ['catalog.json']:
        catalog = read(file)
        catalog['files'] = [f for f in catalog['files'] if f['url'] != DECK]
        catalog['files'].insert(2, dict(title='B2 · Giao tiếp & công việc · 500 từ mới',
            description=f'500 từ mới không trùng các bộ hiện có; {multi} từ có nghĩa/cách dùng phụ. Ví dụ Anh–Việt biên tập riêng, có sẵn offline trên Windows/Android.',
            url=DECK, count=500))
        write(file, catalog)
    attribution = (ROOT / 'decks/B2-DAILY-WORK-ATTRIBUTION.md').read_bytes()
    for file in ['decks/B2-DAILY-WORK-ATTRIBUTION.md']:
        (ROOT / file).write_bytes(attribution)
    print(f'B2 daily/work: {len(deck)} new words; {multi} with {len(secondary)} secondary meanings; '
          f'{500-multi} reviewed exceptions. Public source and catalog updated.')


if __name__ == '__main__':
    main()
