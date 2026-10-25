"""Regression checks for the semantic/structure review, including real regeneration."""
import argparse
import copy
import json
import re
import tempfile
from pathlib import Path
import everyday_extension as extension
from phrase_bundles import sources

ROOT = Path(__file__).resolve().parents[1]
read = lambda path: json.loads(path.read_text(encoding='utf-8'))

def check_preservation():
    original_root = extension.ROOT
    with tempfile.TemporaryDirectory(prefix='semantic-', dir=ROOT.parent/'build') as folder:
        target = Path(folder)
        for name in ['decks/everyday-500.json', 'tools/noun-forms.tsv', 'tools/verb-forms.tsv',
                     'learning/synonyms.json', 'tools/curated-everyday-500-examples.json', 'catalog.json']:
            dest = target/name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((ROOT/name).read_bytes())
        path = target/'decks/everyday-500.json'
        data = read(path)
        match = next(w for w in data if w['word']=='match')
        match.update(senses=[dict(pos='noun', meaningVi='trận đấu', example='The match starts at six.', exampleVi='Trận đấu bắt đầu lúc sáu giờ.')],
                     phrases=[dict(word='match with',pos='verb',meaningVi='phù hợp với')], family=['matching'], editorialNote='Keep this extension')
        expected = copy.deepcopy(match)
        path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
        extension.ROOT = target
        try:
            extension.apply()
            assert next(w for w in read(path) if w['word']=='match') == expected
            first = {p:p.read_bytes() for p in target.rglob('*') if p.is_file()}
            extension.apply()
            assert all(p.read_bytes()==value for p,value in first.items())
        finally:
            extension.ROOT = original_root

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',type=Path)
    args=parser.parse_args()
    decks={p.relative_to(ROOT).as_posix():read(p) for p in sources(ROOT)}
    by={w['word']:w for data in decks.values() for w in data}
    assert 'criteria' not in by and len(by)==6029
    assert {'awl','education'} <= set(by['criterion']['tags'])
    form=next(f for f in by['criterion']['forms'] if f['word']=='criteria')
    assert form['example']=='Applicants are ranked against five published criteria.'
    assert next(s for s in by['mature']['senses'] if 'đáo hạn' in s['meaningVi'])['pos']=='verb'
    assert {f['word'] for f in by['mature']['forms']}=={'matures','maturing','matured'}
    assert by['dark launch']['pos']=='noun' and by['dark launch']['example'].startswith('A dark launch ')
    assert by['double']['synonyms']==['increase twofold'] and by['quadruple']['synonyms']==['increase fourfold']
    proof={r['word']:r for r in read(ROOT/'tools/professional-reading-provenance.json')}
    frames={line.split('|')[0]:line.split('|')[1:] for line in (ROOT/'tools/professional-contexts.tsv').read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')}
    for word in decks['decks/professional-reading-1000.json']:
        p=proof[word['word']]
        if p['contextFrame']=='authored-entry' or word['pos']!='noun':continue
        frame=frames[p['contextFrame']][2*p['contextVariant']]
        assert word['example']==re.sub(r'(?<!the )\{word\}','the {word}',frame,flags=re.I).format(word=word['word'])
    if args.before:
        before=read(args.before)
        allowed={'mature':{'senses','forms'},'criterion':{'tags','forms'},'double':{'synonyms'},'quadruple':{'synonyms'},'dark launch':{'example','exampleVi'}}
        changes=0
        for file,data in decks.items():
            old={w['word']:w for w in before[file]}
            assert set(old)-{w['word'] for w in data}==({'criteria'} if file=='decks/ielts-academic.json' else set())
            for w in data:
                prior=old[w['word']]
                fields={k for k in prior.keys()|w.keys() if prior.get(k)!=w.get(k)}
                permitted={'example'} if file=='decks/professional-reading-1000.json' else allowed.get(w['word'],set())
                assert fields<=permitted,(file,w['word'],fields)
                changes+=bool(fields)
        old_forms={r['word']:r for r in before['learning/word-forms.json']}
        now=read(ROOT/'learning/word-forms.json')
        assert {r['word'] for r in now}-old_forms.keys()=={'mature'}
        for row in now:
            if row['word'] not in {'criterion','mature'}:assert row==old_forms[row['word']],row['word']
        print(f'PASS: {changes} explicitly scoped word updates; criteria is the only removed root; every unrelated lexical field and inflection preserved.')
    check_preservation()
    print('PASS: canonical meaning/POS, contextual synonyms, grammatical frames, criterion/criteria ownership; rebuilding twice retains new senses, phrases, family and editorial metadata.')

if __name__=='__main__':main()
