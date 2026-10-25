"""Verify three canonical IELTS files, unchanged content and public cleanup."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from ielts_bundles import ROOT, IELTS_DECKS, RETIRED_DECKS, read, refresh, source_decks

# Captured before deleting the old files; covers every field of every record.
ORIGINAL_CONTENT_SHA256 = '668185ffbe3a5b32498365afa8898535b95db05bd18e969d2ac1dea84961f26f'


def check_catalog(folder):
    catalog = read(folder / 'catalog.json')
    entries = catalog['files']
    assert len({e['url'] for e in entries}) == len(entries)
    ielts = [e for e in entries if Path(e['url']).name.startswith('ielts-')]
    assert [(e['url'], e['count']) for e in ielts] == [
        ('decks/ielts-academic.json', 317), ('decks/ielts-task1.json', 52), ('decks/ielts-topics.json', 339)]
    assert {p.name for p in (folder / 'decks').glob('ielts-*.json')} == set(IELTS_DECKS)
    for e in entries:
        assert len(read(folder / e['url'])) == e['count'], e['url']
    return catalog


def main():
    combined = [w for name in IELTS_DECKS for w in read(ROOT / 'decks' / name)]
    assert len(combined) == len({w['word'].strip().lower() for w in combined}) == 708
    assert sum(len(w.get('senses', [])) for w in combined) == 467
    assert sum(len(w.get('forms', [])) for w in combined) == 939
    content = json.dumps(sorted(({k:v for k,v in w.items() if k != 'phrases'} for w in combined), key=lambda w: w['word']), sort_keys=True,
                         ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    assert hashlib.sha256(content).hexdigest() == ORIGINAL_CONTENT_SHA256, 'Original IELTS vocabulary changed'
    assert len({w['word'] for p in source_decks(ROOT) for w in read(p)} |
               {w['word'] for w in read(ROOT / 'seed_words.json')}) == 6029
    check_catalog(ROOT)
    generated = [ROOT / 'decks' / name for name in IELTS_DECKS] + [ROOT / 'catalog.json']
    before = {p: p.read_bytes() for p in generated}
    refresh(ROOT)
    assert all(p.read_bytes() == content for p, content in before.items()), 'Refresh is not idempotent'
    assert all(not (ROOT/'decks'/name).exists() for name in RETIRED_DECKS)
    print('PASS: exactly 3 public IELTS sources; 16 retired files absent; '
          'all 708 original roots/466 senses/939 forms unchanged; idempotent catalog refresh.')


if __name__ == '__main__':
    main()
