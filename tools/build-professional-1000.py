"""Build the 700/150/150 reading deck from reviewed local terminology and scenarios."""
import collections
import gzip
import hashlib
import json
import re
import runpy
from pathlib import Path
from vocabulary_tree import owned_entries

ROOT = Path(__file__).resolve().parents[1]
COMMON = runpy.run_path(str(ROOT / 'tools/build-b2-daily-work.py'))
read, write, canonical = (COMMON[k] for k in ['read', 'write', 'canonical'])
DECK = 'decks/professional-reading-1000.json'


def normalized(word):
    return ' '.join(canonical(t) for t in re.sub(r'[-\s]+', ' ', word.strip().lower()).split())


def rows(name):
    return [l.split('|') for l in (ROOT / 'tools' / name).read_text(encoding='utf-8').splitlines()
            if l and not l.startswith('#')]


def main():
    frames = {r[0]: r[1:] for r in rows('professional-contexts.tsv')}
    explicit = {r[0]: r[1:] for r in rows('professional-primary-examples.tsv')}
    overrides = dict(rows('professional-ipa-overrides.tsv'))
    lex = dict(l.split('\t', 1) for l in gzip.decompress(
        (ROOT / 'pronunciation/en-us.tsv.gzip').read_bytes()).decode('utf-8').splitlines())
    prior = {normalized(w['word']) for p in [ROOT / 'seed_words.json',
        *sorted((ROOT / 'decks').glob('*.json'))] if p.name != Path(DECK).name
        for w in owned_entries(p, json.loads(p.read_text(encoding='utf-8')))}
    deck, proof, section, seen = [], [], '', set()
    group_counts = collections.Counter()
    for row in rows('curated-professional-1000.tsv'):
        if row[0].startswith('['):
            section = row[0][1:-1]
            continue
        assert len(row) == 3 and all(s.strip() for s in row), row
        word, pos, meaning = row
        assert pos in COMMON['POS'], (word, pos)
        assert re.fullmatch(r'[a-z]+(?: [a-z]+)*', word), word
        key = normalized(word)
        assert key not in prior | seen, f'Duplicate headword or spelling variant: {word}'
        seen.add(key)
        domain, topic = section.split('/')
        frame_key = 'operations-business' if section == 'business/operations' else topic
        variants = frames[frame_key]
        offset = (group_counts[section] % 2) * 2
        en, vi = variants[offset:offset + 2]
        example = en.format(word=word)
        translation = vi.format(meaning=meaning)
        if word in explicit:
            example, translation = explicit[word]
        readings = []
        tokens = word.split()
        for token in tokens:
            value = overrides.get(token) or lex.get(token)
            assert value and value.startswith('/'), f'Missing IPA: {token}'
            readings.append(value.split(', /')[0].strip('/'))
        ipa = '/' + ' '.join(readings) + '/'
        entry = dict(word=word, ipa=ipa, pos=pos, meaningVi=meaning, example=example,
            exampleVi=translation, topic=domain, level='specialist',
            tags=['professional-reading', domain, topic])
        deck.append(entry)
        proof.append(dict(word=word, section=section, ipaBasis='citation forms of component words; phrase stress not inferred',
            tokenReadings=dict(zip(tokens, readings)), manualTokens=[t for t in tokens if t in overrides],
            contextFrame='authored-entry' if word in explicit else frame_key, contextVariant=offset // 2))
        group_counts[section] += 1
    assert len(deck) == len(seen) == 1000
    assert collections.Counter(w['topic'] for w in deck) == {'technology': 700, 'finance': 150, 'business': 150}
    assert len(group_counts) == 40 and set(group_counts.values()) == {25}
    secondary = rows('curated-professional-secondary.tsv')
    by_word = {w['word']: w for w in deck}
    for row in secondary:
        assert len(row) == 5 and all(s.strip() for s in row)
        word, pos, meaning, en, vi = row
        target = by_word[word]
        assert meaning != target['meaningVi'] and word in en.lower(), word
        target.setdefault('senses', []).append(dict(pos=pos, meaningVi=meaning, ipa=target['ipa'], example=en, exampleVi=vi))
    for file in [DECK]:
        write(file, deck)
    write('tools/professional-reading-provenance.json', proof)
    pairs = [dict(word=w['word'], sourceGroup='professional-reading', **{k: s[k]
        for k in ['pos', 'meaningVi', 'example', 'exampleVi']}) for w in deck for s in [w] + w.get('senses', [])]
    write('tools/curated-professional-examples.json', pairs)
    # Preserve the general lexicon's alternate readings; add only missing surface forms.
    supplement = ''.join(f'{token}\t{ipa}\n' for token, ipa in sorted(overrides.items()) if token not in lex)
    (ROOT / 'pronunciation/specialist-ipa.tsv').write_text(supplement, encoding='utf-8')
    aliases = []
    def sense_id(sense):
        normalized_parts = [re.sub(r'\s+', ' ', sense[k].strip().lower()) for k in ['pos', 'meaningVi']]
        return 'sense:' + hashlib.sha256('\n'.join(normalized_parts).encode()).hexdigest()[:16]
    for original in read('tools/professional-review-preimages.json'):
        before_id, after_id = sense_id(original['before']), sense_id(by_word[original['word']])
        if before_id != after_id:
            aliases.append(dict(word=original['word'], before=before_id, after=after_id))
    assert len(aliases) == 3 and len({a['after'] for a in aliases}) == 3
    assert not {a['after'] for a in aliases} & {a['before'] for a in aliases}
    write('learning/sense-identity-aliases.json', aliases)
    for file in ['catalog.json']:
        catalog = read(file)
        catalog['files'] = [e for e in catalog['files'] if e['url'] != DECK]
        catalog['files'].insert(4, dict(title='Đọc báo công nghệ & AI · 1.000 thuật ngữ',
            description='700 công nghệ/AI, 150 tài chính, 150 doanh nghiệp. Từ và cụm chuyên ngành mới, IPA và ví dụ Anh–Việt; có sẵn offline trên Windows/Android.', url=DECK, count=1000))
        write(file, catalog)
    for file in ['decks/PROFESSIONAL-READING-ATTRIBUTION.md']:
        (ROOT / file).write_bytes((ROOT / 'decks/PROFESSIONAL-READING-ATTRIBUTION.md').read_bytes())
    print(f'Professional reading: 1000 novel terms, 700/150/150, {len(secondary)} secondary uses; {len(prior)+1000} total distinct headwords.')


if __name__ == '__main__':
    main()
