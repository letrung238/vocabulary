"""Verify novelty, ratio, payload identity, pronunciation provenance and reproducibility."""
import collections
import gzip
import hashlib
import json
import runpy
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
builder = runpy.run_path(str(ROOT / 'tools/build-professional-1000.py'))
normalized = builder['normalized']


def read(file):
    return json.loads((ROOT / file).read_text(encoding='utf-8'))


def main():
    deck = read(builder['DECK'])
    assert len(deck) == 1000
    assert collections.Counter(w['topic'] for w in deck) == {'technology': 700, 'finance': 150, 'business': 150}
    prior = [w for p in [ROOT / 'seed_words.json', *sorted((ROOT / 'decks').glob('*.json'))]
             if p.name != 'professional-reading-1000.json' for w in json.loads(p.read_text(encoding='utf-8'))]
    prior_ids = {normalized(w['word']) for w in prior}
    ids = {normalized(w['word']) for w in deck}
    assert len(ids) == 1000 and not ids & prior_ids
    catalog_words = {w['word'] for entry in read('catalog.json')['files'] for w in read(entry['url'])}
    assert {w['word'] for w in prior + deck} == catalog_words, 'Sources differ from the current public catalog'
    assert sum(len(w.get('senses', [])) for w in deck) == 32
    proof = {r['word']: r for r in read('tools/professional-reading-provenance.json')}
    assert set(proof) == {w['word'] for w in deck}
    pairs = read('tools/curated-professional-examples.json')
    assert len(pairs) == 1032
    lookup = {(r['word'], r['pos'], r['meaningVi']): r for r in pairs}
    assert len(lookup) == len(pairs)
    for word in deck:
        assert word['level'] == 'specialist' and 'professional-reading' in word['tags']
        assert word['ipa'] == '/' + ' '.join(proof[word['word']]['tokenReadings'][t] for t in word['word'].split()) + '/'
        for sense in [word] + word.get('senses', []):
            for field in ['ipa', 'pos', 'meaningVi', 'example', 'exampleVi']:
                assert isinstance(sense.get(field), str) and sense[field].strip(), (word['word'], field)
            assert word['word'] in sense['example'].lower(), word['word']
            r = lookup[(word['word'], sense['pos'], sense['meaningVi'])]
            assert (r['example'], r['exampleVi']) == (sense['example'], sense['exampleVi'])
    by_word = {w['word']: w for w in deck}
    assert 'ˈɪn.ɪt' in by_word['init container']['ipa']
    assert 'riːd' in by_word['sequential read']['ipa']
    assert 'đạo hàm' in by_word['derivative']['senses'][0]['meaningVi']
    assert 'trạng thái' in by_word['response time']['meaningVi']
    assert by_word['out of distribution']['pos'] == 'adjective'
    assert 'inputs were out of distribution' in by_word['out of distribution']['example']
    assert 'the same aspect' in by_word['mobile chipset']['example']
    assert 'không giữ chỗ' in by_word['reserved instance']['exampleVi']
    assert 'watt' in by_word['power consumption']['meaningVi']
    assert 'từng phần' in by_word['serialization']['senses'][0]['meaningVi']
    assert 'ảnh hưởng' in by_word['cipher']['senses'][0]['meaningVi']
    base = dict(line.split('\t', 1) for line in gzip.decompress((ROOT / 'pronunciation/en-us.tsv.gzip').read_bytes()).decode().splitlines())
    supplement = dict(line.split('\t', 1) for line in (ROOT / 'pronunciation/specialist-ipa.tsv').read_text(encoding='utf-8').splitlines())
    assert not base.keys() & supplement.keys(), 'Supplement must preserve existing homograph readings'
    component_tokens = {t for w in deck for t in w['word'].split()}
    missing_before = component_tokens - base.keys()
    assert len(missing_before) == 61 and missing_before <= supplement.keys()
    aliases = read('learning/sense-identity-aliases.json')
    patches = read('learning/content-corrections.json')
    assert len(aliases) == 3
    for alias in aliases:
        p = next(p for p in patches if p['word'] == alias['word'])
        def sense_id(s):
            normalized = lambda text: ' '.join(text.lower().split())
            return 'sense:' + hashlib.sha256((normalized(s['pos']) + '\n' + normalized(s['meaningVi'])).encode()).hexdigest()[:16]
        assert alias['before'] == sense_id(p['before']) and alias['after'] == sense_id(p['after'])
    targets = [builder['DECK'],
        'tools/professional-reading-provenance.json', 'tools/curated-professional-examples.json',
        'catalog.json', 'pronunciation/specialist-ipa.tsv',
        'learning/sense-identity-aliases.json']
    for file in ['catalog.json']:
        entries = [e for e in read(file)['files'] if e['url'] == builder['DECK']]
        assert len(entries) == 1 and entries[0]['count'] == 1000
    before = {file: hashlib.sha256((ROOT / file).read_bytes()).digest() for file in targets}
    # The shipped deck includes reviewed corrections, forms and synonyms applied
    # after the raw terminology builder. Verify the complete publishing pipeline.
    subprocess.run([sys.executable, str(ROOT / 'tools/enrich-learning-content.py')], check=True)
    assert all(hashlib.sha256((ROOT / file).read_bytes()).digest() == digest for file, digest in before.items())
    print(f'PASS: 1000 novel reading terms, 700/150/150, 1032 bilingual contexts, 61 restored component IPA, 3 stable sense identities, idempotent reviewed rebuild; {len(catalog_words)} current catalog roots.')


if __name__ == '__main__':
    main()
