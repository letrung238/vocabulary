"""Regression checks for the language errors found during the JSON review."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from vocabulary_tree import entries as tree_entries

ROOT = Path(__file__).resolve().parents[1]


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f'Duplicate JSON key: {key}'
        result[key] = value
    return result


def read(file):
    return json.loads((ROOT / file).read_text(encoding='utf-8-sig'), object_pairs_hook=unique_object,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))


def main():
    paths = subprocess.check_output(['rg', '--files', '-g', '*.json'], cwd=ROOT, text=True).splitlines()
    excluded = {'build', 'bin', 'obj', 'dist', 'node_modules', '.gradle'}
    paths = [p for p in paths if not excluded.intersection(Path(p).parts)]
    for path in paths:
        read(path)
    files = ['seed_words.json'] + [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / 'decks').glob('*.json'))]
    by_file = {f: {w['word']: w for w in tree_entries(read(f))} for f in files}
    forbidden = ['The bad news distract him', 'She scream when', 'She felt puzzle', 'at the small came',
                 'hurt her arm in the upper jaw', 'room felt everlasting', 'moved severely through',
                 'Community service reoffends', 'mold kept the bread fresh']
    for file, words in by_file.items():
        for w in words.values():
            meanings = set()
            for s in [w] + w.get('senses', []):
                assert not re.search(r'\bbut see\b', s['meaningVi'], re.I), (file, w['word'])
                key = s.get('pos', '').strip().lower(), s['meaningVi'].strip().lower()
                assert key not in meanings, f'Repeated sense: {file} {w["word"]}'
                meanings.add(key)
                assert s.get('example', '').strip() and s.get('exampleVi', '').strip(), (file, w['word'])
                assert not any(bad in s['example'] for bad in forbidden), (file, w['word'])
                if s.get('ipa'):
                    assert s['ipa'].startswith('/') and s['ipa'].endswith('/'), (file, w['word'], s['ipa'])
    b2 = by_file['decks/b2-1000.json']
    assert 'khô' in b2['waterproof']['exampleVi'] and 'ướt' not in b2['waterproof']['exampleVi']
    assert 'hông' in b2['hip']['exampleVi'] and 'gối' not in b2['hip']['exampleVi']
    assert 'hai chấm' in b2['colon']['exampleVi'] and 'phẩy' not in b2['colon']['exampleVi']
    assert 'tam giác đều' in b2['triangle']['exampleVi']
    assert b2['graphic']['pos'] == b2['proposition']['pos'] == 'noun'
    assert b2['content']['ipa'] == '/kənˈtent/' and b2['insult']['ipa'] == '/ˈɪn.sʌlt/'
    assert b2['polish']['ipa'] == '/ˈpɒl.ɪʃ/' and 'độ bóng' in b2['polish']['exampleVi']
    assert b2['ally']['ipa'] == '/ˈæl.aɪ/' and b2['ally']['senses'][0]['ipa'] == '/əˈlaɪ/'
    assert b2['multiply']['ipa'] == '/ˈmʌl.tɪ.plaɪ/' and b2['multiply']['senses'][0]['ipa'] == '/ˈmʌl.tə.pli/'
    refuse = by_file[files[0]]['refuse']
    assert refuse['ipa'] == '/rɪˈfjuːz/' and refuse['senses'][0]['ipa'] == '/ˈref.juːs/'
    assert len(read('decks/it-advanced.json')) == 151
    patches = read('learning/content-corrections.json')
    assert len(patches) == 225
    assert sum(p['file'] == 'decks/professional-reading-1000.json' for p in patches) == 20
    for patch in patches:
        word = by_file[patch['file']][patch['word']]
        expected = {k: word.get(k, '') for k in ['pos', 'meaningVi', 'example', 'exampleVi', 'ipa']}
        assert patch['after'] == expected, (patch['file'], patch['word'])
        actual = [{k: s.get(k, '') for k in expected} for s in word.get('senses', [])]
        assert patch['afterSenses'] == actual, (patch['file'], patch['word'])
    for file in ['catalog.json']:
        actual = sum(bool(w.get('senses')) for w in by_file[files[0]].values())
        assert f'{actual} từ có nghĩa phụ' in read(file)['files'][0]['description']
    # Verify regeneration rather than merely asserting that it should be repeatable.
    tracked = [ROOT / p for p in paths] + [ROOT / 'tools/sense-exceptions.txt']
    hashes = {p: hashlib.sha256(p.read_bytes()).digest() for p in tracked}
    subprocess.run([sys.executable, str(ROOT / 'tools/enrich-learning-content.py')], cwd=ROOT, check=True)
    assert all(hashlib.sha256(p.read_bytes()).digest() == digest for p, digest in hashes.items()), 'Regeneration changed reviewed content'
    print(f'PASS: {len(paths)} public source JSON, reviewed language regressions, sense IPA, catalog and idempotent regeneration.')


if __name__ == '__main__':
    main()
