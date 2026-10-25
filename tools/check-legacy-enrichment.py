"""Verify approved legacy additions, complete morphology and preservation."""
import argparse
import json
import re
import runpy
from pathlib import Path
from legacy_enrichment import phrases, senses
from morphology_rules import EXCLUDED_VERBS
from phrase_bundles import sources
from vocabulary_tree import entries

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
key=lambda s:(s['pos'],s['meaningVi'])

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--before',type=Path);args=parser.parse_args()
    roots=[w for path in sources(ROOT) for w in read(path)]
    by={}
    for w in entries(roots):by.setdefault(w['word'],w)
    scope=read(ROOT/'tools/legacy-review-scope.json')
    restored=read(ROOT/'tools/restored-v1-words.json');restored_names={w['word'] for w in restored}
    assert len(restored_names)==10 and set(scope['firstWords'])<=by.keys()
    assert len(set(scope['expandedWords'])|set(scope['firstWords']))==1020
    for w in restored:
        for k in ['pos','ipa','meaningVi','example','exampleVi']:assert by[w['word']][k]==w[k],(w['word'],k)
    authored=phrases();names={p['word'] for p in authored}
    assert len(names)==108 and not names&{w['word'] for w in roots}
    for p in authored:
        actual=by[p['word']]
        assert {k:v for k,v in actual.items() if k!='forms'}==p,p['word']
        owners=[w for w in roots if any(c['word']==p['word'] for c in w.get('phrases',[]))]
        assert len(owners)==1 and owners[0]['word']==p['word'].split()[0]
        choices=[p['word']]+[f['word'] for f in actual.get('forms',[])]
        assert any(re.search(r'(?<![a-z])'+re.escape(f)+r'(?![a-z])',p['example'].lower()) for f in choices),p['word']
        if p['pos']=='verb':assert len(actual.get('forms',[]))>=3,p['word']
    assert len(senses())==56
    for s in senses():
        actual=next(v for v in by[s['word']].get('senses',[]) if key(v)==key(s))
        assert (actual['example'],actual['exampleVi'])==(s['example'],s['exampleVi'])
        if s['ipa']:assert actual['ipa']==s['ipa']
    edits=read(ROOT/'tools/curated-legacy-synonyms.json');assert len(edits)==94
    for r in edits:
        w=by[r['word']];assert key(w)==key(r)
        assert set(r['synonyms'])<=set(w['synonyms'])
        if r['mode']=='replace':assert w['synonyms']==r['synonyms']
    builder=runpy.run_path(str(ROOT/'tools/build-word-forms.py'))
    payload=read(ROOT/'learning/word-forms.json');assert payload==builder['build_payload']()
    table={l.split('\t')[0] for l in (ROOT/'tools/verb-forms.tsv').read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')}
    assert not table&EXCLUDED_VERBS and table==set(builder['verbs']())
    for name,expected in {'empty':{'empties','emptying','emptied'},'query':{'queries','querying','queried'},
                          'suggest':{'suggests','suggesting','suggested'},'consider':{'considers','considering','considered'}}.items():
        assert {f['word'] for f in by[name]['forms']}==expected,name
    if args.before:
        baseline=read(args.before);old_names={w['word'] for data in baseline.values() for w in data}
        synonyms={r['word']:r for r in edits}
        assert {w['word'] for w in roots}-old_names==restored_names
        for filename,data in baseline.items():
            current={w['word']:w for w in read(Path(filename))}
            for old in data:
                new=current[old['word']]
                for k in ['pos','ipa','meaningVi','example','exampleVi']:assert new[k]==old[k],(old['word'],k)
                change=synonyms.get(old['word'])
                expected=old['synonyms'] if change is None else change['synonyms'] if change['mode']=='replace' else list(dict.fromkeys(old['synonyms']+change['synonyms']))
                assert new['synonyms']==expected,(old['word'],'unapproved synonym change')
                for s in old.get('senses',[]):assert s in new.get('senses',[]),(old['word'],'lost sense')
                for child in old.get('phrases',[]):assert child in new.get('phrases',[]),(old['word'],'changed prior phrase')
                for f in old.get('forms',[]):
                    now=next(g for g in new['forms'] if g['word']==f['word'])
                    assert set(f['types'])<=set(now['types']),(old['word'],f['word'])
                    assert set(f.get('ipa','').split(', '))<=set(now.get('ipa','').split(', ')),(old['word'],f['word'],'ipa')
                    for k in ['example','exampleVi']:
                        if f.get(k):assert now.get(k)==f[k],(old['word'],f['word'],k)
        print('PASS: every prior primary field, secondary sense, phrase, inflection type/IPA and bilingual form context preserved; only the 10 original v1 roots restored.')
    print('PASS: 1020 early lemmas covered; 10 v1 roots restored, 108 nested phrases, 56 secondary meanings, 94 exact-primary synonym updates; shared exclusions and reproducible inflections.')

if __name__=='__main__':main()
