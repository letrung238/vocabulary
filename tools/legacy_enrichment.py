"""Reviewed enrichment of the original v1/v2 vocabulary, not new vocabulary guesses."""
import copy
from pathlib import Path
from ielts_bundles import read, write, source_decks
from vocabulary_tree import entries
from morphology_rules import EXCLUDED_VERBS

ROOT=Path(__file__).resolve().parents[1]
TAILS={'for':'fər','to':'tə','of':'əv','from':'frəm','about':'əˈbaʊt','as':'æz','with':'wɪð',
       'against':'əˈɡenst','at':'æt','upon':'əˈpɑːn','in':'ɪn','on':'ɑːn','into':'ˈɪntuː',
       'between':'bɪˈtwiːn','that':'ðæt','through':'θruː'}

def rows(name,root=ROOT):
    return [line.split('|') for line in (root/'tools'/name).read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')]

def senses(root=ROOT):
    return [dict(word=w,pos=p,ipa=i,meaningVi=m,example=e,exampleVi=v)
            for w,p,i,m,e,v in rows('curated-legacy-senses.tsv',root)]

def phrases(root=ROOT):
    known={}
    for path in [root/'seed_words.json',*source_decks(root)]:
        for word in read(path):known.setdefault(word['word'],word)
    extras=senses(root)
    result=[]
    for phrase,pos,meaning,en,vi in rows('curated-legacy-phrases.tsv',root):
        head,*tail=phrase.split();parent=known[head]
        choices=[s for s in [parent]+parent.get('senses',[])+[s for s in extras if s['word']==head] if s['pos']==pos]
        assert choices,(phrase,'Missing reviewed parent/POS')
        ipa=(choices[0].get('ipa') or parent['ipa']).strip('/')
        topic=parent.get('topic') or 'common'
        result.append(dict(word=phrase,pos=pos,ipa='/'+ipa+' '+' '.join(TAILS[t] for t in tail)+'/',meaningVi=meaning,
            example=en,exampleVi=vi,topic=topic,tags=['prepositions','legacy-reviewed',topic],synonyms=[]))
    return result

def table_updates(path, additions, excluded=()):
    lines=[line for line in path.read_text(encoding='utf-8').splitlines() if line.split('\t')[0] not in excluded]
    known={line.split('\t')[0] for line in lines if line and not line.startswith('#')}
    lines += ['\t'.join(row) for row in additions if row[0] not in known]
    value='\n'.join(lines)+'\n'
    if path.read_text(encoding='utf-8')!=value:path.write_text(value,encoding='utf-8')

def regular(head):
    # Every added head is a reviewed regular verb; never infer irregular verbs.
    third=head+'es' if head.endswith(('s','x','z','ch','sh')) else head+'s'
    ing=head[:-1]+'ing' if head.endswith('e') else head+'ing'
    past=head+'d' if head.endswith('e') else head+'ed'
    if head.endswith('y') and head[-2] not in 'aeiou':third,past=head[:-1]+'ies',head[:-1]+'ied'
    return [third,ing,past,past]

def prepare(root=ROOT):
    seed_path=root/'seed_words.json';seed=read(seed_path)
    present={w['word'] for p in [seed_path,*source_decks(root)] for w in read(p)}
    restored=read(root/'tools/restored-v1-words.json')
    seed += [copy.deepcopy(w) for w in restored if w['word'] not in present]
    write(seed_path,seed)
    all_words=[w for p in [seed_path,*source_decks(root)] for w in entries(read(p))]
    new_senses=senses(root)
    by_name={w['word']:w for w in all_words}
    new_phrases=phrases(root)
    # This curation owns these new definitions; retain forms and other extensions.
    authored={w['word']:w for w in new_phrases}
    for path in [seed_path,*source_decks(root)]:
        data=read(path)
        for word in entries(data):
            if word['word'] in authored:
                word.update({k:authored[word['word']][k] for k in ['pos','ipa','meaningVi','example','exampleVi']})
        write(path,data)
    verb_names={w['word'] for w in all_words if any(s['pos']=='verb' for s in [w]+w.get('senses',[]))}
    verb_names|={s['word'] for s in new_senses if s['pos']=='verb'}
    verb_names|={w['word'] for w in new_phrases if w['pos']=='verb'}
    verb_names -= EXCLUDED_VERBS
    table=root/'tools/verb-forms.tsv'
    prior={line.split('\t')[0]:line.split('\t')[1:] for line in table.read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')}
    added=[]
    for name in sorted(verb_names-prior.keys(),key=lambda w:(' ' in w,w)):
        head,*tail=name.split()
        columns=prior.get(head) or regular(head)
        if tail:columns=[','.join(part+' '+' '.join(tail) for part in column.split(',')) for column in columns]
        added.append([name,*columns]);prior[name]=columns
    table_updates(table,added,EXCLUDED_VERBS)
    noun_names={w['word'] for w in all_words if any(s['pos']=='noun' for s in [w]+w.get('senses',[]))}
    noun_names|={s['word'] for s in new_senses if s['pos']=='noun'}
    noun_names|={w['word'] for w in new_phrases if w['pos']=='noun'}
    table=root/'tools/noun-forms.tsv'
    prior={line.split('\t')[0]:line.split('\t')[1:] for line in table.read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')}
    # Newly introduced nouns have a countable sense. Existing countability decisions win.
    added=[]
    for name in sorted(noun_names-prior.keys(),key=lambda w:(' ' in w,w)):
        head,*tail=name.split()
        plural=head[:-1]+'ies' if head.endswith('y') and head[-2] not in 'aeiou' else head+'es' if head.endswith(('s','x','z','ch','sh')) else head+'s'
        status,index,forms=prior.get(head,['countable','0',plural])
        if tail:forms=','.join(p+' '+' '.join(tail) for p in forms.split(',')) if forms else ''
        added.append([name,status,index,forms]);prior[name]=[status,index,forms]
    table_updates(table,added)
    examples=[dict(word=w['word'],sourceGroup='legacy-v1',**{k:w[k] for k in ['pos','meaningVi','example','exampleVi']}) for w in restored]
    write(root/'tools/curated-legacy-examples.json',examples)
    import runpy
    builder=runpy.run_path(str(root/'tools/build-prepositions.py'))
    all_phrases=builder['build']()
    write(root/'learning/phrase-roots.json',builder['phrase_roots'](all_phrases))
    path=root/'tools/curated-prepositions-examples.json';contexts=read(path)
    keys={(r['word'],r['pos'],r['meaningVi']) for r in contexts}
    for w in new_phrases:
        identity=(w['word'],w['pos'],w['meaningVi'])
        if identity in keys:
            record=next(r for r in contexts if (r['word'],r['pos'],r['meaningVi'])==identity)
            record.update(example=w['example'],exampleVi=w['exampleVi'])
        else:
            contexts.append(dict(word=w['word'],sourceGroup='prepositions',**{k:w[k] for k in ['pos','meaningVi','example','exampleVi']}))
    write(path,contexts)
    catalog=read(root/'catalog.json');catalog['files'][0]['count']=len(seed)
    phrase_entry=next(e for e in catalog['files'] if e['url']=='decks/prepositions.json')
    phrase_entry['description']=f"32 từ gốc bổ sung cùng các cụm liên quan và idiom care of. Các cụm khác nằm ngay trong từ gốc ở bộ tương ứng. Bộ offline Windows/Android nhập đủ {len(all_phrases)} cụm."
    write(root/'catalog.json',catalog)

def apply(decks,edit,root=ROOT):
    owners={}
    for file,words in decks.items():
        for word in words:owners.setdefault(word['word'],(file,word))
    for record in senses(root):
        file,word=owners[record['word']]
        if any(s['pos']==record['pos'] and s['meaningVi']==record['meaningVi'] for s in [word]+word.get('senses',[])):continue
        value={k:v for k,v in record.items() if k!='word' and (k!='ipa' or v)}
        edit(file,word['word'],senses=word.get('senses',[])+[value])
    for record in read(root/'tools/curated-legacy-synonyms.json'):
        file,word=owners[record['word']]
        assert (word['pos'],word['meaningVi'])==(record['pos'],record['meaningVi']),record['word']
        values=record['synonyms'] if record['mode']=='replace' else list(dict.fromkeys(word['synonyms']+record['synonyms']))
        assert len(values)<=4,word['word']
        edit(file,word['word'],synonyms=values)
    path=root/'learning/synonyms.json';curated=read(path)
    selected={r['word'] for r in read(root/'tools/curated-legacy-synonyms.json')}|{r['word'] for r in read(root/'tools/restored-v1-words.json')}
    for word in [owners[name][1] for name in sorted(selected)]+phrases(root):
        key=(word['word'],word['pos'],word['meaningVi'])
        record=next((r for r in curated if (r['word'],r['pos'],r['meaningVi'])==key),None)
        if record is None:
            record=dict(word=word['word'],pos=word['pos'],meaningVi=word['meaningVi'],source='gpt-edited');curated.append(record)
        record.update(synonyms=word['synonyms'],reason='' if word['synonyms'] else 'Chưa có từ đồng nghĩa phổ biến phù hợp đúng nghĩa và từ loại.')
    write(path,sorted(curated,key=lambda r:(r['word'].lower(),r['pos'],r['meaningVi'])))
