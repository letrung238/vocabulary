"""Rebuild the intermediate supplement from frozen, reviewed local sources."""
import json
import re
import runpy
from pathlib import Path
from vocabulary_tree import owned_entries

ROOT = Path(__file__).resolve().parents[1]
COMMON = runpy.run_path(str(ROOT / 'tools/build-b2-daily-work.py'))
read, write, rows, canonical = (COMMON[k] for k in ['read', 'write', 'rows', 'canonical'])
DECK = 'decks/daily-work-498.json'
BASIC = {'work', 'book', 'make', 'get', 'have', 'do', 'eat', 'drink', 'buy', 'see', 'count', 'print'}


def main():
    primary = rows('curated-daily-work-498-primary.tsv')
    secondary = rows('curated-daily-work-498-secondary.tsv')
    proof = read('tools/daily-work-498-provenance.json')
    evidence = {r['word']: r for r in proof}
    assert len(primary) == len(proof) == len(evidence) == 498
    assert {r[0] for r in primary} == set(evidence)
    existing = {canonical(w['word']) for path in [ROOT / 'seed_words.json',
                *sorted((ROOT / 'decks').glob('*.json'))] if path.name != Path(DECK).name
                for w in owned_entries(path, json.loads(path.read_text(encoding='utf-8')))}
    words = {}
    seen = set()
    for row in primary:
        assert len(row) == 7 and all(x.strip() for x in row), row
        word, pos, ipa, meaning, example, translation, topic = row
        key = canonical(word)
        assert key not in existing | seen and word not in BASIC, f'Duplicate/basic word: {word}'
        assert re.fullmatch(r'[a-z]+', word), word
        record = evidence[word]
        assert record['ipaReviewed'] and record['ipa'] == ipa and record['primaryPos'] == pos
        assert record['level'] in ['B1', 'B2']
        assert any(e['level'] == record['level'] and e['pos'] == pos for e in record['levelEvidence']), word
        assert ipa.startswith('/') and ipa.endswith('/'), word
        words[word] = dict(word=word, ipa=ipa, pos=pos, meaningVi=meaning, example=example,
            exampleVi=translation, level=record['level'], topic=topic,
            tags=[record['level'].lower(), 'daily-work', 'daily-work-498', topic])
        seen.add(key)
    for row in secondary:
        assert len(row) in (5, 6) and all(x.strip() for x in row), row
        word, pos, meaning, example, translation = row[:5]
        target = words[word]
        ipa = row[5] if len(row) == 6 else target['ipa']
        assert ipa.startswith('/') and ipa.endswith('/'), word
        assert pos in COMMON['POS'], (word, pos)
        identities = {(s['pos'], s['meaningVi']) for s in [target] + target.get('senses', [])}
        assert (pos, meaning) not in identities and meaning != target['meaningVi'], word
        target.setdefault('senses', []).append(dict(pos=pos, meaningVi=meaning,
            example=example, exampleVi=translation, ipa=ipa))
    deck = list(words.values())
    assert len(secondary) == 320 and sum(bool(w.get('senses')) for w in deck) == 227
    for path in [DECK]:
        write(path, deck)
    pairs = [dict(word=w['word'], sourceGroup='daily-work-498', **{k: s[k]
             for k in ['pos', 'meaningVi', 'example', 'exampleVi']})
             for w in deck for s in [w] + w.get('senses', [])]
    write('tools/curated-daily-work-498-examples.json', pairs)
    for file in ['catalog.json']:
        catalog = read(file)
        catalog['files'] = [f for f in catalog['files'] if f['url'] != DECK]
        catalog['files'].insert(3, dict(title='Giao tiếp & công việc · 498 từ trung cấp',
            description='498 từ mới, tránh từ quá cơ bản và không trùng các bộ cũ. Nhãn nguồn B1/B2; 227 từ có nghĩa/cách dùng phụ, 818 ví dụ Anh–Việt; có sẵn offline trên Windows/Android.',
            url=DECK, count=498))
        write(file, catalog)
    attribution = (ROOT / 'decks/DAILY-WORK-498-ATTRIBUTION.md').read_bytes()
    for path in ['decks/DAILY-WORK-498-ATTRIBUTION.md']:
        (ROOT / path).write_bytes(attribution)
    core = read('seed_words.json') + read('decks/b2-1000.json') + read('decks/b2-daily-work-500.json') + deck
    assert len(core) == len({canonical(w['word']) for w in core}) == 3010
    print('Daily/work: 498 new intermediate words; 227 with 320 secondary uses; '
          '271 reviewed exceptions. Core selection: 3000 distinct words.')


if __name__ == '__main__':
    main()
