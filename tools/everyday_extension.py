"""The second 500 authored everyday lemmas; merged into the existing public deck."""
import copy
import json
from pathlib import Path
from ielts_bundles import read, write

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'tools/curated-everyday-extra-500.tsv'

def rows():
    result = [line.split('|') for line in SOURCE.read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')]
    assert len(result) == len({row[0] for row in result}) == 500
    assert all(len(row)==10 for row in result)
    return result

def names():
    return {row[0] for row in rows()}

def build():
    result = [dict(word=w,pos=p,ipa=i,meaningVi=m,example=e,exampleVi=v,topic=t,
                 tags=['everyday-extra-500',t],synonyms=s.split(';') if s else [])
            for w,p,i,m,e,v,t,status,forms,s in rows()]
    path = ROOT/'decks/everyday-500.json'
    existing = {w['word']:w for w in read(path)} if path.exists() else {}
    # The TSV owns primary fields. Secondary senses, phrases and other editorial
    # extensions belong to the canonical deck; morphology is applied separately.
    for word in result:
        for key, value in existing.get(word['word'], {}).items():
            if key not in word and key != 'forms':
                word[key] = copy.deepcopy(value)
    return result

def noun_rows():
    result={}
    for word,pos,ipa,meaning,en,vi,topic,policy,forms,synonyms in rows():
        if pos!='noun': continue
        status={'c':'countable','m':'mass','i':'invariant','p':'lexical_plural'}[policy[0]]
        plural=(policy.partition(':')[2] or
                (word[:-1]+'ies' if word.endswith('y') and word[-2] not in 'aeiou' else
                 word+'es' if word.endswith(('s','x','z','ch','sh')) else word+'s')) if status=='countable' else word if status=='invariant' else ''
        result[word]=[word,status,'0',plural]
    assert len(result)==350
    return result

def verb_rows():
    result=[[row[0],*row[8].split(',')] for row in rows() if row[1]=='verb']
    assert len(result)==50 and all(len(row)==5 for row in result)
    return result

def update_table(path, additions):
    selected={row[0] for row in additions}
    old=[line for line in path.read_text(encoding='utf-8').splitlines() if line.split('\t')[0] not in selected]
    content='\n'.join(old+['\t'.join(row) for row in additions])+'\n'
    if path.read_text(encoding='utf-8')!=content: path.write_text(content,encoding='utf-8')

def apply():
    additions=build()
    selected=names()
    path=ROOT/'decks/everyday-500.json'
    current=read(path)
    old=[word for word in current if word['word'] not in selected]
    assert len(old)==500, 'Keep the original 500 everyday roots intact'
    existing={word['word']:word for word in current}
    for word in additions:
        if existing.get(word['word'],{}).get('forms'):
            word['forms']=existing[word['word']]['forms']
    write(path,old+additions)
    update_table(ROOT/'tools/noun-forms.tsv',list(noun_rows().values()))
    update_table(ROOT/'tools/verb-forms.tsv',verb_rows())
    path=ROOT/'learning/synonyms.json'
    records=[record for record in read(path) if record['word'] not in selected]
    for word in additions:
        records.append(dict(word=word['word'],pos=word['pos'],meaningVi=word['meaningVi'],synonyms=word['synonyms'],
            reason='' if word['synonyms'] else 'Chưa xác định từ đồng nghĩa phổ biến phù hợp với đúng nghĩa và từ loại này.',source='gpt-edited'))
    write(path,sorted(records,key=lambda row:(row['word'].lower(),row['pos'],row['meaningVi'])))
    path=ROOT/'tools/curated-everyday-500-examples.json'
    secondary = {(w['word'], s['pos'], s['meaningVi']) for w in additions for s in w.get('senses', [])}
    contexts=[record for record in read(path) if record['word'] not in selected or
              (record['word'],record['pos'],record['meaningVi']) in secondary]
    contexts.extend(dict(word=word['word'],sourceGroup='everyday-500',
        **{key:word[key] for key in ['pos','meaningVi','example','exampleVi']}) for word in additions)
    write(path,contexts)
    path=ROOT/'catalog.json'
    catalog=read(path)
    entry=next(row for row in catalog['files'] if row['url']=='decks/everyday-500.json')
    entry.update(title='Đời sống · 1.000 từ',count=1000,
        description='1.000 từ gốc, gồm hai đợt 500 từ không trùng kho trước đó. 1.083 ngữ cảnh Anh–Việt, IPA, dạng chia và đồng nghĩa theo nghĩa. Có sẵn offline trên Windows/Android; nhập lại giữ tiến độ và nội dung cá nhân.')
    write(path,catalog)

if __name__=='__main__':
    apply()
