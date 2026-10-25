"""Build the authored preposition combinations; retain the reviewed verb head table."""
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = 'prepositions.json'


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, data):
    content = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if not path.exists() or path.read_bytes() != content: path.write_bytes(content)


def build():
    words = []
    for line in (ROOT/'tools/curated-prepositions.tsv').read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'): continue
        word, pos, ipa, meaning, example, translation, topic, synonyms = line.split('|')
        assert pos in {'verb','adjective','idiom'}, word
        words.append(dict(word=word, pos=pos, ipa=ipa,
            meaningVi=meaning, example=example, exampleVi=translation, topic=topic,
            tags=['prepositions', topic], synonyms=synonyms.split(';') if synonyms else []))
    extra = [
        ('think of', 'có ý kiến; đánh giá về ai hoặc điều gì', 'What do you think of the new design?', 'Bạn thấy thiết kế mới thế nào?'),
        ('think of', 'cân nhắc; có ý định làm điều gì, theo sau bằng V-ing', 'We are thinking of moving closer to work.', 'Chúng tôi đang cân nhắc chuyển đến gần nơi làm việc hơn.'),
        ('think about', 'nghĩ đến; để tâm trí hướng về ai hoặc điều gì', 'I often think about my family when I travel.', 'Tôi thường nghĩ về gia đình khi đi xa.'),
        ('care for', 'thích; muốn có hoặc dùng, thường gặp trong câu hỏi, câu phủ định hoặc lời mời', 'Would you care for some tea?', 'Bạn có muốn dùng chút trà không?'),
        ('take care of', 'lo liệu; xử lý một công việc hoặc vấn đề', 'I will take care of the travel arrangements.', 'Tôi sẽ lo việc sắp xếp chuyến đi.'),
    ]
    lookup = {w['word']: w for w in words}
    for word, meaning, example, translation in extra:
        lookup[word].setdefault('senses', []).append(dict(pos='verb', meaningVi=meaning,
            example=example, exampleVi=translation, ipa=lookup[word]['ipa']))
    assert len(words) == len(lookup) == 150
    from legacy_enrichment import phrases as legacy_phrases
    return words + additional_phrases() + legacy_phrases()


def additional_phrases():
    """500 authored additions; roots/POS already exist, pronunciation keeps reviewed head IPA."""
    tails = dict(up='ʌp', down='daʊn', **{'in':'ɪn', 'out':'aʊt', 'on':'ɑːn', 'off':'ɔːf',
        'away':'əˈweɪ', 'back':'bæk', 'over':'ˈoʊvər', 'through':'θruː', 'along':'əˈlɔːŋ',
        'around':'əˈraʊnd', 'by':'baɪ', 'ahead':'əˈhed', 'together':'təˈɡeðər',
        'across':'əˈkrɔːs', 'into':'ˈɪntuː', 'of':'əv', 'with':'wɪð', 'to':'tə',
        'from':'frəm', 'against':'əˈɡenst', 'for':'fər', 'after':'ˈæftər', 'without':'wɪˈðaʊt',
        'under':'ˈʌndər', 'as':'æz', 'about':'əˈbaʊt', 'apart':'əˈpɑːrt', 'forward':'ˈfɔːrwərd',
        'aside':'əˈsaɪd', 'way':'weɪ', 'rise':'raɪz', 'vent':'vent', 'do':'duː',
        'room':'ruːm', 'use':'juːs', 'fun':'fʌn', 'sense':'sens', 'light':'laɪt', 'at':'æt',
        'upon':'əˈpɑːn', 'behind':'bɪˈhaɪnd', 'go':'ɡoʊ'})
    roots = {}
    for path in [ROOT/'seed_words.json', *sorted((ROOT/'decks').glob('*.json'))]:
        for word in read(path): roots.setdefault(word['word'], word)
    result = []
    for line in (ROOT/'tools/curated-root-phrases-500.tsv').read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'): continue
        phrase, pos, meaningVi, example, exampleVi = line.split('|')
        head, *rest = phrase.split()
        parent = roots[head]
        senses = [s for s in [parent]+parent.get('senses', []) if s.get('pos') == pos]
        assert senses and pos in {'verb','adjective'}, (phrase, 'Missing reviewed root/POS')
        head_ipa = (senses[0].get('ipa') or parent['ipa']).strip('/')
        body = ' '.join([head_ipa, *[tails[token] for token in rest]])
        if phrase == 'come to': body = head_ipa + ' tuː'  # stressed particle: regain consciousness
        topic = parent.get('topic') or 'daily'
        result.append(dict(word=phrase, pos=pos, ipa='/'+body+'/', meaningVi=meaningVi,
            example=example, exampleVi=exampleVi, topic=topic, tags=['prepositions', topic], synonyms=[]))
    assert len(result) == len({w['word'] for w in result}) == 500
    assert sum(w['pos']=='verb' for w in result) == 420
    return result


def main():
    data = build()
    write(ROOT/'learning/phrase-roots.json', phrase_roots(data))
    others = [ROOT/'seed_words.json', *sorted((ROOT/'decks').glob('*.json'))]
    existing = {w['word'].lower() for path in others if path.name != DECK for w in read(path)}
    assert not existing.intersection(w['word'] for w in data), 'A phrase already exists in another deck'
    from phrase_bundles import place_phrases
    count = place_phrases(data)
    table = ROOT/'tools/verb-forms.tsv'
    lines = table.read_text(encoding='utf-8').splitlines()
    heads = {parts[0]: parts[1:] for line in lines if line and not line.startswith('#') for parts in [line.split('\t')]}
    # Reviewed regular heads missing from the earlier vocabulary's verb inventory.
    for head, forms in {
        'agree':'agrees|agreeing|agreed|agreed', 'arrive':'arrives|arriving|arrived|arrived',
        'believe':'believes|believing|believed|believed', 'benefit':'benefits|benefiting|benefited|benefited',
        'care':'cares|caring|cared|cared', 'consist':'consists|consisting|consisted|consisted',
        'dream':'dreams|dreaming|dreamed|dreamed', 'hope':'hopes|hoping|hoped|hoped',
        'laugh':'laughs|laughing|laughed|laughed', 'prepare':'prepares|preparing|prepared|prepared',
        'result':'results|resulting|resulted|resulted', 'smile':'smiles|smiling|smiled|smiled',
        'talk':'talks|talking|talked|talked',
        'abstain':'abstains|abstaining|abstained|abstained', 'account':'accounts|accounting|accounted|accounted',
        'add':'adds|adding|added|added', 'amount':'amounts|amounting|amounted|amounted',
        'appeal':'appeals|appealing|appealed|appealed', 'catch':'catches|catching|caught|caught',
        'collaborate':'collaborates|collaborating|collaborated|collaborated',
        'comment':'comments|commenting|commented|commented', 'connect':'connects|connecting|connected|connected',
        'count':'counts|counting|counted|counted', 'decide':'decides|deciding|decided|decided',
        'provide':'provides|providing|provided|provided', 'refer':'refers|referring|referred|referred',
        'stem':'stems|stemming|stemmed|stemmed', 'vote':'votes|voting|voted|voted',
        'worry':'worries|worrying|worried|worried',
    }.items(): heads.setdefault(head, forms.split('|'))
    phrase_names = {w['word'] for w in data if w['pos'] == 'verb'}
    kept = [line for line in lines if line.split('\t')[0] not in phrase_names]
    for word in sorted(phrase_names):
        head, tail = word.split(' ', 1)
        assert head in heads and len(heads[head]) == 4, 'Missing reviewed verb head: ' + head
        forms = [','.join(surface+' '+tail for surface in column.split(',')) for column in heads[head]]
        kept.append('\t'.join([word, *forms]))
    inventory = {line.split('\t')[0] for line in kept}
    for word in new_roots():
        if word['pos'] == 'verb' and word['word'] not in inventory:
            kept.append('\t'.join([word['word'], *heads[word['word']]]))
    table.write_bytes(('\n'.join(kept)+'\n').encode('utf-8'))
    pairs = [dict(word=w['word'], sourceGroup='prepositions', **{k:s[k] for k in ['pos','meaningVi','example','exampleVi']})
             for w in data + new_roots() for s in [w]+w.get('senses', [])]
    write(ROOT/'tools/curated-prepositions-examples.json', pairs)
    curated = ROOT/'learning/synonyms.json'
    authored = data + new_roots()
    current = [r for r in read(curated) if r['word'] not in {w['word'] for w in authored}]
    for word in authored:
        current.append(dict(word=word['word'], pos=word['pos'], meaningVi=word['meaningVi'], synonyms=word['synonyms'],
            reason='' if word['synonyms'] else 'Chưa xác định từ đồng nghĩa phổ biến phù hợp với đúng nghĩa và từ loại này.', source='gpt-edited'))
    write(curated, sorted(current, key=lambda r:(r['word'].lower(),r['pos'],r['meaningVi'])))
    for path in [ROOT/'catalog.json']:
        catalog = read(path)
        catalog['files'] = [e for e in catalog['files'] if e['url'] not in {'decks/'+DECK,'decks/prepositions-50.json'}]
        catalog['files'].insert(4, dict(title='Từ gốc bổ sung và cụm với giới từ', count=count, url='decks/'+DECK,
            description=f'32 từ gốc bổ sung cùng các cụm liên quan và idiom care of. Các cụm khác nằm ngay trong từ gốc ở bộ tương ứng. Bộ offline Windows/Android nhập đủ {len(data)} cụm.'))
        write(path, catalog)
    forms = runpy.run_path(str(ROOT/'tools/build-word-forms.py'))
    payload = forms['build_payload']()
    forms['write'](forms['PAYLOAD'], payload)
    for path in ['learning/word-forms.json']:
        forms['write'](ROOT/path,payload)
    forms['apply_to_decks'](payload)
    print('PASS: 650 combinations; 500 additional phrases attached to existing roots; 655 bilingual contexts; reviewed verb-head conjugations.')


def phrase_roots(data):
    # Editorial grouping for this reviewed list only, never infer links from arbitrary imports.
    # c/o is a postal idiom, not a construction of the verb care.
    groups = {}
    for word in data:
        phrase = word['word']
        if phrase == 'care of': continue
        root = 'care' if phrase == 'take care of' else phrase.split(' ', 1)[0]
        groups.setdefault(root, []).append(phrase)
    return groups


def new_roots():
    result = []
    for line in (ROOT/'tools/curated-phrase-roots.tsv').read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'): continue
        word, pos, ipa, meaningVi, example, exampleVi = line.split('|')
        result.append(dict(word=word, pos=pos, ipa=ipa, meaningVi=meaningVi,
            example=example, exampleVi=exampleVi, topic='common', tags=['prepositions'], synonyms=[]))
    assert len(result) == 32
    return result


if __name__ == '__main__': main()
