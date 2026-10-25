"""Build the approved 500-entry deck from frozen local GPT-edited content."""
import gzip
import hashlib
import json
import re
import runpy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DECK='everyday-500.json'
PROPOSAL=ROOT/'tools/approved-everyday-500.md'
IPA_FILE=ROOT/'tools/everyday-500-ipa.json'

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path,data):
    from phrase_bundles import retain_children
    retain_children(path, data)
    value=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if not path.exists() or path.read_text(encoding='utf-8')!=value: path.write_text(value,encoding='utf-8')
def rows(path): return [l.split('|') for l in path.read_text(encoding='utf-8').splitlines() if l and not l.startswith('#')]

def proposed():
    result=[]
    for line in PROPOSAL.read_text(encoding='utf-8').splitlines():
        match=re.fullmatch(r'\| (\d+) \| ([^|]+) \| ([^|]+) \|',line)
        if match: result.append((int(match[1]),match[2].strip(),match[3].strip()))
    fingerprint=hashlib.sha256(json.dumps(result,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    assert fingerprint=='97e2f97a3d355368b1fea6dda8d114b232978afdb053da60f7c0a43bf2fa2742', 'Approved proposal identities changed'
    return result

IPA_OVERRIDES={
    'do':'/duː/','go':'/ɡoʊ/','come':'/kʌm/','put':'/pʊt/','let':'/let/','say':'/seɪ/',
    'eat':'/iːt/','drink':'/drɪŋk/','sleep':'/sliːp/','watch':'/wɑtʃ/','walk':'/wɔk/',
    'run':'/rʌn/','stand':'/stænd/','wear':'/wer/','drive':'/draɪv/','ride':'/raɪd/',
    'meet':'/miːt/','start':'/stɑrt/','stop':'/stɑp/','wait':'/weɪt/','learn':'/lɜrn/',
    'teach':'/tiːtʃ/','live':'/lɪv/','love':'/lʌv/','like':'/laɪk/','call':'/kɔl/',
    'move':'/muːv/','turn':'/tɜrn/','hold':'/hoʊld/','carry':'/ˈkæri/','send':'/send/',
    'receive':'/rɪˈsiːv/','win':'/wɪn/','lose':'/luːz/','build':'/bɪld/','break':'/breɪk/',
    'cut':'/kʌt/','show':'/ʃoʊ/','feel':'/fiːl/','happen':'/ˈhæpən/','become':'/bɪˈkʌm/',
    'understand':'/ˌʌndərˈstænd/','seem':'/siːm/','stay':'/steɪ/','return':'/rɪˈtɜrn/',
    'change':'/tʃeɪndʒ/','look':'/lʊk/','see':'/siː/','hear':'/hɪr/','touch':'/tʌtʃ/',
    'duvet':'/duːˈveɪ/','strainer':'/ˈstreɪnər/','bedsheet':'/ˈbedʃiːt/',
    'pillowcase':'/ˈpɪloʊkeɪs/','dishcloth':'/ˈdɪʃklɔθ/','hoodie':'/ˈhʊdi/',
    'waistcoat':'/ˈweɪstkoʊt/','tracksuit':'/ˈtræksuːt/','toothache':'/ˈtuːθeɪk/',
    'stomachache':'/ˈstʌməkeɪk/','barcode':'/ˈbɑrkoʊd/','postbox':'/ˈpoʊstbɑks/',
    'postcode':'/ˈpoʊstkoʊd/','payslip':'/ˈpeɪslɪp/','stepbrother':'/ˈstepbrʌðər/',
    'T-shirt':'/ˈtiː ʃɜrt/','update':'/ˈʌpdeɪt/','suit':'/suːt/',
    'mother-in-law':'/ˈmʌðər ɪn lɔ/','father-in-law':'/ˈfɑðər ɪn lɔ/',
    'son-in-law':'/ˈsʌn ɪn lɔ/','daughter-in-law':'/ˈdɔtər ɪn lɔ/',
    'brother-in-law':'/ˈbrʌðər ɪn lɔ/','sister-in-law':'/ˈsɪstər ɪn lɔ/',
    'half-brother':'/ˈhæf brʌðər/','half-sister':'/ˈhæf sɪstər/',
    'bank transfer':'/ˈbæŋk ˌtrænsfɜr/','diarrhea':'/ˌdaɪəˈriə/',
    'windy':'/ˈwɪndi/','emergency room':'/ɪˈmɜrdʒənsi ˈruːm/',
    'great-grandmother':'/ˌɡreɪtˈɡrændˌmʌðər/',
    'overpriced':'/ˌoʊvərˈpraɪst/','baggage carousel':'/ˈbæɡədʒ ˌkærəˈsel/'
}

def freeze_ipa():
    lexicon=dict(line.split('\t',1) for line in gzip.decompress((ROOT/'pronunciation/en-us.tsv.gzip').read_bytes()).decode().splitlines())
    def reading(word):
        result=lexicon.get(word.lower())
        assert result, f'Missing offline IPA: {word}'
        body=result.split(', ')[0].strip('/').replace('ɹ','r').replace('ɫ','l').replace('ɛ','e')
        # CMU uses AH for both STRUT and schwa, and ER for both stressed and
        # unstressed rhotic vowels. Resolve only the vowel after each stress.
        cluster=r'([ˈˌ][^aeiouyæɑɔeɪʊəʌɜɝɚ]*)'
        body=re.sub(cluster+'ə',r'\1ʌ',body)
        body=re.sub(cluster+'ɝ',r'\1ɜr',body)
        return body.replace('ɝ','ər').replace('ɚ','ər')
    result={}
    for _,word,_ in proposed():
        value=IPA_OVERRIDES.get(word)
        if not value:
            value='/'+(reading(word) if word.lower() in lexicon else ' '.join(reading(p) for p in re.split(r'[ -]',word)))+'/'
        result[word]=value
    write(IPA_FILE,result)

PRIMARY_MEANINGS={'call':'gọi điện','turn':'rẽ','lose':'mất; làm mất','return':'trở về',
    'pepper':'ớt; quả ớt','purse':'ví','free':'rảnh','hard':'cứng','old':'già',
    'host':'chủ nhà; người đón khách'}
ADJECTIVES={'striped','checked','tight','fashionable','out of stock','in stock','sold out','secondhand','brand-new','overpriced'}

def build():
    pronunciation=read(IPA_FILE)
    contexts=rows(ROOT/'tools/curated-everyday-500-primary.tsv')
    assert [int(r[0]) for r in contexts]==list(range(1,501))
    deck=[]
    for (index,word,meaning),(index2,example,translation,synonyms) in zip(proposed(),contexts):
        assert index==int(index2)
        topic=next(t for end,t in [(50,'daily'),(100,'home'),(150,'food'),(190,'clothing'),(240,'health'),(290,'shopping'),(340,'travel'),(390,'work'),(450,'daily'),(500,'family')] if index<=end)
        pos='verb' if index<=50 or word=='sneeze' else 'adjective' if 391<=index<=450 or word in ADJECTIVES else 'noun'
        deck.append(dict(word=word,pos=pos,ipa=pronunciation[word],meaningVi=PRIMARY_MEANINGS.get(word,meaning),
            example=example,exampleVi=translation,topic=topic,tags=['everyday-500',topic],
            synonyms=synonyms.split(';') if synonyms else []))
    by_word={w['word']:w for w in deck}
    for word,pos,ipa,meaning,example,translation in rows(ROOT/'tools/curated-everyday-500-secondary.tsv'):
        w=by_word[word]
        w.setdefault('senses',[]).append(dict(pos=pos,ipa=ipa or w['ipa'],meaningVi=meaning,example=example,exampleVi=translation))
    assert len(deck)==len(by_word)==500
    from everyday_extension import build as extension
    return deck + extension()

VERBS="""
do|does|doing|did|done
go|goes|going|went|gone
come|comes|coming|came|come
put|puts|putting|put|put
let|lets|letting|let|let
say|says|saying|said|said
eat|eats|eating|ate|eaten
drink|drinks|drinking|drank|drunk
sleep|sleeps|sleeping|slept|slept
watch|watches|watching|watched|watched
walk|walks|walking|walked|walked
run|runs|running|ran|run
stand|stands|standing|stood|stood
wear|wears|wearing|wore|worn
drive|drives|driving|drove|driven
ride|rides|riding|rode|ridden
meet|meets|meeting|met|met
start|starts|starting|started|started
stop|stops|stopping|stopped|stopped
wait|waits|waiting|waited|waited
learn|learns|learning|learned,learnt|learned,learnt
teach|teaches|teaching|taught|taught
live|lives|living|lived|lived
love|loves|loving|loved|loved
like|likes|liking|liked|liked
call|calls|calling|called|called
move|moves|moving|moved|moved
turn|turns|turning|turned|turned
hold|holds|holding|held|held
carry|carries|carrying|carried|carried
send|sends|sending|sent|sent
receive|receives|receiving|received|received
win|wins|winning|won|won
lose|loses|losing|lost|lost
build|builds|building|built|built
break|breaks|breaking|broke|broken
cut|cuts|cutting|cut|cut
show|shows|showing|showed|shown,showed
feel|feels|feeling|felt|felt
happen|happens|happening|happened|happened
become|becomes|becoming|became|become
understand|understands|understanding|understood|understood
seem|seems|seeming|seemed|seemed
stay|stays|staying|stayed|stayed
return|returns|returning|returned|returned
change|changes|changing|changed|changed
look|looks|looking|looked|looked
see|sees|seeing|saw|seen
hear|hears|hearing|heard|heard
touch|touches|touching|touched|touched
cushion|cushions|cushioning|cushioned|cushioned
whisk|whisks|whisking|whisked|whisked
toast|toasts|toasting|toasted|toasted
suit|suits|suiting|suited|suited
ring|rings|ringing|rang|rung
bruise|bruises|bruising|bruised|bruised
itch|itches|itching|itched|itched
cash|cashes|cashing|cashed|cashed
parcel|parcels|parceling,parcelling|parceled,parcelled|parceled,parcelled
update|updates|updating|updated|updated
free|frees|freeing|freed|freed
light|lights|lighting|lit,lighted|lit,lighted
cool|cools|cooling|cooled|cooled
host|hosts|hosting|hosted|hosted
sneeze|sneezes|sneezing|sneezed|sneezed
"""
MASS=set('say|sleep|wear|love|housework|corn|shrimp|salmon|tuna|cream|honey|vinegar|cooking oil|olive oil|soy sauce|mustard|ketchup|mayonnaise|jam|peanut butter|porridge|cereal|toast|bacon|cotton|wool|linen|leather|skin|blood|dizziness|nausea|swelling|ointment|vaccination|postage|cash|store credit|customer service|car rental|currency exchange|passport control|checked baggage|excess baggage|lost property|left luggage|sick leave|annual leave|paid leave|unpaid leave|overtime pay|reimbursement|remote work|hybrid work|time off|clarification|permission|work experience|employment history|light'.split('|'))
# Jam/ toast acquire plural labels only for their separately authored count senses.
MASS-= {'jam','toast','skin','shrimp','salmon','tuna','clarification'}
MASS.update({'ride-sharing','diarrhea','constipation'})
MASS.discard('swelling')  # The authored definition also includes a countable swollen area.
INVARIANT={'shrimp','salmon','tuna'}
LEXICAL_PLURAL={'tongs','trousers','sunglasses','sweatpants','leggings','tights','flexible hours','meeting minutes'}
IRREGULAR_PLURAL={'knife':'knives','calf':'calves','child':'children','grandchild':'grandchildren','wife':'wives','half-brother':'half-brothers'}
PLURAL_IPA={
    'mother-in-law':('/ˈmʌðərz ɪn lɔ/',), 'father-in-law':('/ˈfɑðərz ɪn lɔ/',),
    'son-in-law':('/ˈsʌnz ɪn lɔ/',), 'daughter-in-law':('/ˈdɔtərz ɪn lɔ/',),
    'brother-in-law':('/ˈbrʌðərz ɪn lɔ/',), 'sister-in-law':('/ˈsɪstərz ɪn lɔ/',),
    'half-brother':('/ˈhæf brʌðərz/',),'calf':('/kævz/',),'child':('/ˈtʃɪldrən/',),'wife':('/waɪvz/',),
    'grandchild':('/ˈɡræntʃɪldrən/',)
}

def plural(word):
    if word in IRREGULAR_PLURAL: return IRREGULAR_PLURAL[word]
    if word.endswith('-in-law'): return word[:-7]+'s-in-law'
    head=word.split()[-1]
    changed=head[:-1]+'ies' if head.endswith('y') and head[-2] not in 'aeiou' else head+'es' if head.endswith(('s','x','z','ch','sh')) else head+'s'
    return ' '.join(word.split()[:-1]+[changed])

def update_table(path,new_rows):
    keys={r[0] for r in new_rows}
    old=[line for line in path.read_text(encoding='utf-8').splitlines() if line.split('\t')[0] not in keys]
    value='\n'.join(old+['\t'.join(r) for r in new_rows])+'\n'
    if path.read_text(encoding='utf-8')!=value: path.write_text(value,encoding='utf-8')

if __name__=='__main__':
    from everyday_extension import apply as apply_extension, noun_rows as extension_nouns
    apply_extension()
    if not IPA_FILE.exists(): freeze_ipa()
    data=build()
    for path in [ROOT/'decks'/DECK]: write(path,data)
    update_table(ROOT/'tools/verb-forms.tsv',[line.split('|') for line in VERBS.strip().splitlines()])
    write(ROOT/'tools/everyday-500-plural-ipa.json',{base:dict(word=plural(base),ipa=values[0]) for base,values in PLURAL_IPA.items()})
    nouns=[]
    new_nouns=extension_nouns()
    for w in data:
        if not any(s['pos']=='noun' for s in [w]+w.get('senses',[])): continue
        word=w['word']
        if word in new_nouns:
            nouns.append(new_nouns[word]); continue
        status='mass' if word in MASS else 'lexical_plural' if word in LEXICAL_PLURAL else 'invariant' if word in INVARIANT else 'countable'
        nouns.append([word,status,str(len(word.split())-1),word if status=='invariant' else plural(word) if status=='countable' else ''])
    update_table(ROOT/'tools/noun-forms.tsv',nouns)
    pairs=[dict(word=w['word'],sourceGroup='everyday-500',**{k:s[k] for k in ('pos','meaningVi','example','exampleVi')}) for w in data for s in [w]+w.get('senses',[])]
    write(ROOT/'tools/curated-everyday-500-examples.json',pairs)
    curated=['curated-sense-examples.json','curated-awl-examples.json','curated-b2-examples.json','curated-core-examples.json',
        'curated-b2-daily-work-examples.json','curated-daily-work-498-examples.json','curated-professional-examples.json',
        'curated-reviewed-examples.json','curated-basic-20-examples.json','curated-basic-120-examples.json','curated-everyday-500-examples.json','curated-prepositions-examples.json']
    write(ROOT/'learning/sense-examples.json',sum((read(ROOT/'tools'/name) for name in curated),[]))
    for path in [ROOT/'catalog.json']:
        catalog=read(path)
        entry=next(f for f in catalog['files'] if f['url']=='decks/'+DECK)
        entry.update(title='Đời sống · 1.000 từ',count=1000,
            description='1.000 từ gốc với 1.083 ngữ cảnh Anh–Việt, IPA, dạng chia và đồng nghĩa phù hợp; có sẵn offline trên Windows/Android.')
        write(path,catalog)
    forms=runpy.run_path(str(ROOT/'tools/build-word-forms.py'))
    payload=forms['build_payload'](); forms['write'](forms['PAYLOAD'],payload)
    for path in ['learning/word-forms.json']: forms['write'](ROOT/path,payload)
    forms['apply_to_decks'](payload)
    # Exact preimages allow installed decks to remove only the known shipped errors.
    corrected={w['word']:w for w in read(ROOT/'decks'/DECK)}
    sense=lambda w:{k:w.get(k,'') for k in ('pos','meaningVi','ipa','example','exampleVi')}
    repairs=[dict(file='decks/'+DECK,word=old['word'],reason='Reviewed everyday vocabulary correction',
        before=sense(old),after=sense(corrected[old['word']]),
        beforeSenses=old.get('senses',[]),afterSenses=corrected[old['word']].get('senses',[]),
        beforeForms=old.get('forms',[]),afterForms=corrected[old['word']].get('forms',[]))
        for old in read(ROOT/'tools/everyday-500-before-review.json')]
    write(ROOT/'learning/everyday-corrections.json',repairs)
    target=ROOT/'learning/content-corrections.json'
    write(target,sorted([r for r in read(target) if r['file']!='decks/'+DECK]+repairs,key=lambda r:(r['file'],r['word'])))
    for path in ['learning/everyday-corrections.json']:
        write(ROOT/path,repairs)
    print(f'PASS: built 1000 approved roots (500 new) and {len(pairs)} bilingual contexts, offline IPA and reviewed forms.')
