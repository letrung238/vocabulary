"""Attach reviewed verb/noun inflections without adding vocabulary records.

Default builds are offline. Refresh the frozen table with lemminflect==0.2.3:
    python tools/build-word-forms.py --refresh-table --apply
After language editing, rerun with --apply to update public canonical decks.
"""
import argparse
import collections
import gzip
import json
import re
from pathlib import Path
from vocabulary_tree import entries as tree_entries
from ielts_bundles import source_decks, refresh as refresh_ielts, write as write_json

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / 'tools/verb-forms.tsv'
PAYLOAD = ROOT / 'learning/word-forms.json'
NOUN_TABLE = ROOT / 'tools/noun-forms.tsv'
NOUN_RENAMES = ROOT / 'tools/noun-renames.json'
_PLURAL_IPA_FILE = ROOT / 'tools/everyday-500-plural-ipa.json'
REVIEWED_PLURAL_IPA = json.loads(_PLURAL_IPA_FILE.read_text(encoding='utf-8')) if _PLURAL_IPA_FILE.exists() else {}
TAGS = ('VBZ', 'VBG', 'VBD', 'VBN')
TYPES = dict(VBZ=['present_third_person_singular'], VBG=['present_participle', 'gerund'],
             VBD=['past_simple'], VBN=['past_participle'])
from morphology_rules import EXCLUDED_VERBS as EXCLUDED
# Dictionary alternatives that depend on meaning are selected against the source
# definitions. Other overrides cover reviewed specialist verbs absent in the dictionary.
OVERRIDES = {
    'bid': 'bids|bidding|bid|bid', 'weave': 'weaves|weaving|wove|woven',
    'relay': 'relays|relaying|relayed|relayed', 'hang': 'hangs|hanging|hung|hung',
    'wind': 'winds|winding|wound|wound', 'dare': 'dares|daring|dared|dared',
    'screen share': 'screen shares|screen sharing|screen shared|screen shared',
    'fulfil': 'fulfils|fulfilling|fulfilled|fulfilled',
    'fulfill': 'fulfills|fulfilling|fulfilled|fulfilled',
    'enrol': 'enrols|enrolling|enrolled|enrolled',
    'occur': 'occurs|occurring|occurred|occurred',
    'install': 'installs|installing|installed|installed',
    'target': 'targets|targeting|targeted|targeted',
    'cc': "cc's|cc'ing|cc'd,cc'ed|cc'd,cc'ed",
    'initial': 'initials|initialing,initialling|initialed,initialled|initialed,initialled',
    'broadcast': 'broadcasts|broadcasting|broadcast,broadcasted|broadcast,broadcasted',
    'forecast': 'forecasts|forecasting|forecast,forecasted|forecast,forecasted',
    'lean': 'leans|leaning|leaned,leant|leaned,leant',
    'spill': 'spills|spilling|spilled,spilt|spilled,spilt',
    'spoil': 'spoils|spoiling|spoiled,spoilt|spoiled,spoilt',
    'dial': 'dials|dialing,dialling|dialed,dialled|dialed,dialled',
    'channel': 'channels|channeling,channelling|channeled,channelled|channeled,channelled',
}
REGULAR_OVERRIDES = {
    'anonymize': 'anonymizes|anonymizing|anonymized|anonymized',
    'cabin': 'cabins|cabining|cabined|cabined',
    'carpool': 'carpools|carpooling|carpooled|carpooled',
    'debounce': 'debounces|debouncing|debounced|debounced',
    'denormalize': 'denormalizes|denormalizing|denormalized|denormalized',
    'deprioritize': 'deprioritizes|deprioritizing|deprioritized|deprioritized',
    'district': 'districts|districting|districted|districted',
    'eagle': 'eagles|eagling|eagled|eagled',
    'expense': 'expenses|expensing|expensed|expensed',
    'flavour': 'flavours|flavouring|flavoured|flavoured',
    'fleet': 'fleets|fleeting|fleeted|fleeted',
    'hood': 'hoods|hooding|hooded|hooded',
    'jitter': 'jitters|jittering|jittered|jittered',
    'minify': 'minifies|minifying|minified|minified',
    'onboard': 'onboards|onboarding|onboarded|onboarded',
    'peach': 'peaches|peaching|peached|peached',
    'refactor': 'refactors|refactoring|refactored|refactored',
    'remediate': 'remediates|remediating|remediated|remediated',
    'romance': 'romances|romancing|romanced|romanced',
    'sunset': 'sunsets|sunsetting|sunsetted|sunsetted',
    'supersede': 'supersedes|superseding|superseded|superseded',
    'theme': 'themes|theming|themed|themed',
    'torch': 'torches|torching|torched|torched',
    'whiteboard': 'whiteboards|whiteboarding|whiteboarded|whiteboarded',
    'widow': 'widows|widowing|widowed|widowed',
}
OVERRIDES.update(REGULAR_OVERRIDES)
ALTERNATIVES = {'cancel', 'canal', 'caravan', 'devil', 'funnel', 'gossip', 'label',
                'parallel', 'rival', 'tunnel', 'worship', 'fuel', 'queue', 'queue up', 'cue'}
VERB_IPA = {
    'accent': '/əkˈsent/', 'addict': '/əˈdɪkt/', 'aggregate': '/ˈæɡ.rɪ.ɡeɪt/',
    'ally': '/əˈlaɪ/', 'alternate': '/ˈɔːl.tə.neɪt/',
    'appropriate': '/əˈprəʊ.pri.eɪt/', 'approximate': '/əˈprɒk.sɪ.meɪt/',
    'attribute': '/əˈtrɪb.juːt/', 'bow': '/baʊ/', 'compact': '/kəmˈpækt/',
    'compound': '/kəmˈpaʊnd/', 'conduct': '/kənˈdʌkt/', 'conflict': '/kənˈflɪkt/',
    'console': '/kənˈsəʊl/', 'contract': '/kənˈtrækt/', 'contrast': '/kənˈtrɑːst/',
    'convict': '/kənˈvɪkt/', 'defect': '/dɪˈfekt/', 'deliberate': '/dɪˈlɪb.ə.reɪt/',
    'digest': '/daɪˈdʒest/', 'export': '/ɪkˈspɔːt/', 'extract': '/ɪkˈstrækt/',
    'frequent': '/friˈkwent/', 'graduate': '/ˈɡrædʒ.u.eɪt/', 'import': '/ɪmˈpɔːt/',
    'incline': '/ɪnˈklaɪn/', 'insult': '/ɪnˈsʌlt/', 'legitimate': '/lɪˈdʒɪt.ə.meɪt/',
    'moderate': '/ˈmɒd.ə.reɪt/', 'object': '/əbˈdʒekt/', 'permit': '/pəˈmɪt/',
    'progress': '/prəˈɡres/', 'project': '/prəˈdʒekt/', 'refuse': '/rɪˈfjuːz/',
    'relay': '/ˌrɪˈleɪ/', 'resume': '/rɪˈzjuːm/', 'suspect': '/səˈspekt/',
    'survey': '/səˈveɪ/', 'wind': '/waɪnd/',
}
IRREGULAR_IPA = {'stridden': '/ˈstrɪd.ən/', 'underlay': '/ˌʌn.dəˈleɪ/',
                 'underlain': '/ˌʌn.dəˈleɪn/', 'spoilt': '/spɔɪlt/',
                 'wound': '/waʊnd/', 'leapt': '/lept/', 'read': '/red/', 'heard': '/hɜrd/'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    write_json(path, value)


def sources():
    return [ROOT / 'seed_words.json', *source_decks(ROOT)]


def normalize_nouns(records):
    """Explicit, reviewed renames only; never infer a lemma by removing -s."""
    renames = {r['renameFrom']: r for r in read(NOUN_RENAMES)}
    existing = {w['word'] for w in records}
    for word in records:
        r = renames.get(word['word'])
        if not r or r['word'] in existing:
            continue
        assert (word['pos'], word['meaningVi']) == (r['pos'], r['meaningVi'])
        assert not word.get('senses'), 'Rename needs a separate review of secondary meanings'
        word.update({k: r[k] for k in ('word', 'ipa', 'example', 'exampleVi')})
        if r.get('lemmaMeaningVi'):
            word['meaningVi'] = r['lemmaMeaningVi']
    return records


def nouns():
    result = {}
    for path in sources():
        for word in tree_entries(normalize_nouns(read(path))):
            senses = [s for s in [word] + word.get('senses', []) if s.get('pos') == 'noun']
            if senses:
                result.setdefault(word['word'], (word, []))[1].extend(senses)
    return result


def applicable_forms(word, forms):
    positions = {s.get('pos') for s in [word] + word.get('senses', [])}
    result = []
    for form in forms:
        types = [t for t in form['types'] if ('noun' if t == 'plural' else 'verb') in positions]
        if types:
            copy = dict(form, types=types)
            combined = 'plural' in form['types'] and any(t != 'plural' for t in form['types'])
            if combined and len(positions & {'noun', 'verb'}) == 1:
                readings = re.findall(r'/[^/]+/', form['ipa'])
                copy['ipa'] = readings[-1] if 'noun' in positions else readings[0]
            # A verb sentence does not illustrate a noun-only sense even when
            # the plural has the same spelling as third-person singular.
            if 'verb' not in positions and any(t != 'plural' for t in form['types']):
                copy.pop('example', None); copy.pop('exampleVi', None)
            result.append(copy)
    return result


def noun_ipa(base, surface, head_index, entry, lexicon):
    if base in REVIEWED_PLURAL_IPA:
        reviewed=REVIEWED_PLURAL_IPA[base]
        assert surface==reviewed['word'], 'Plural identity changed: '+base
        return reviewed['ipa']
    if base == 'mouth' and surface == 'mouths': return '/maʊðz/'
    word, senses = entry
    body = (senses[0].get('ipa') or word['ipa']).strip('/')
    if surface == base:
        return '/' + body + '/'
    head, changed = base.split()[head_index], surface.split()[head_index]
    # Compound IPA is tokenized like the reviewed headword. Inflect the noun
    # head, not a plural complement: boards of directors, systems on a chip.
    bits = body.split(' ')
    assert len(base.split()) == len(bits) or head_index == len(base.split()) - 1, (base, body)
    index = head_index if len(base.split()) == len(bits) else len(bits) - 1
    stem = bits[index]
    if changed in {head + 's', head + 'es', head[:-1] + 'ies'}:
        # house compounds voice /s/ in the plural: greenhouses, warehouses.
        if head.endswith('house') and stem.endswith('s'):
            stem = stem[:-1] + 'z'
        # Rhotic/voicing glyphs used by the existing offline dictionary.
        ending = 'ɪz' if stem.endswith(('s','z','ʃ','ʒ','tʃ','dʒ')) else 's' if stem.endswith(('p','t','k','f','θ')) else 'z'
        bits[index] = stem + ending
        return '/' + ' '.join(bits) + '/'
    overrides = {
        'analyses': '/əˈnæləsiːz/', 'axes': '/ˈæksiːz/', 'bacteria': '/bækˈtɪəriə/',
        'bases': '/ˈbeɪsiːz/', 'crises': '/ˈkraɪsiːz/', 'criteria': '/kraɪˈtɪəriə/',
        'diagnoses': '/ˌdaɪəɡˈnəʊsiːz/', 'emphases': '/ˈemfəsiːz/',
        'hypotheses': '/haɪˈpɒθəsiːz/', 'theses': '/ˈθiːsiːz/',
        'spokespeople': '/ˈspəʊksˌpiːpəl/', 'ling': '/lɪŋ/',
        'radii': '/ˈreɪdiaɪ/', 'syllabi': '/ˈsɪləbaɪ/',
    }
    reading = overrides.get(changed) or lexicon.get(changed)
    assert reading, f'Missing noun plural IPA: {base}/{surface}'
    return ', '.join('/' + ' '.join(bits[:index] + [r] + bits[index+1:]) + '/'
                     for r in re.findall(r'/([^/]+)/', reading))


def verbs():
    result = {}
    for path in sources():
        for word in tree_entries(read(path)):
            senses = [s for s in [word] + word.get('senses', []) if s.get('pos') == 'verb']
            if senses and word['word'] not in EXCLUDED:
                result.setdefault(word['word'], (word, senses))
    return result


def refresh_table(entries):
    from lemminflect import getInflection
    from importlib.metadata import version
    assert version('lemminflect') == '0.2.3'
    lines = ['# LemmInflect 0.2.3 + reviewed overrides; VBZ/VBG/VBD/VBN; no OOV guesses.']
    for base in sorted(entries):
        if base in OVERRIDES:
            columns = OVERRIDES[base].split('|')
        else:
            head, *tail = base.split()
            columns = []
            for tag in TAGS:
                forms = getInflection(head, tag, inflect_oov=False)
                assert forms, f'Needs review: {base}/{tag}'
                if base not in ALTERNATIVES:
                    forms = forms[:1]
                columns.append(','.join(' '.join([f, *tail]) for f in forms))
        lines.append('\t'.join([base, *columns]))
    TABLE.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def regular_past(base, surface):
    return surface in {base + 'ed', base + 'd', base + base[-1] + 'ed', base[:-1] + 'ied', base + 'ked'}


def ipa(base, surface, tag, entry, lexicon):
    word, senses = entry
    if base == 'screen share':
        head, changed, body, prefix, suffix = 'share', surface.split()[1], 'ʃeər', 'skriːn ', ''
    else:
        head, *tail = base.split()
        changed = surface.split()[0]
        body = (VERB_IPA.get(base) or senses[0].get('ipa') or word['ipa']).strip('/')
        prefix, suffix = '', ''
        if tail:
            body, remainder = body.split(' ', 1)
            suffix = ' ' + remainder
    if head == 'read' and tag in ('VBD', 'VBN'):
        return '/' + prefix + 'red' + suffix + '/'
    if tag in ('VBD', 'VBN') and changed in IRREGULAR_IPA:
        return '/' + prefix + IRREGULAR_IPA[changed].strip('/') + suffix + '/'
    if tag == 'VBZ' and head in {'be', 'do', 'have', 'say'}:
        return '/' + prefix + {'be': 'ɪz', 'do': 'dʌz', 'have': 'hæz', 'say': 'sez'}[head] + suffix + '/'
    if changed == head:
        return '/' + prefix + body + suffix + '/'
    if tag == 'VBZ':
        ending = 'ɪz' if body.endswith(('s', 'z', 'ʃ', 'ʒ', 'tʃ', 'dʒ')) else 's' if body.endswith(('p', 't', 'k', 'f', 'θ')) else 'z'
    elif tag == 'VBG':
        ending = 'ɪŋ'
    elif regular_past(head, changed) or (head == 'cc' and changed in {"cc'd", "cc'ed"}):
        ending = 'ɪd' if body.endswith(('t', 'd')) else 't' if body.endswith(('p', 'k', 'f', 'θ', 's', 'ʃ', 'tʃ')) else 'd'
    else:
        reading = IRREGULAR_IPA.get(changed) or lexicon.get(changed)
        assert reading, f'Missing irregular IPA: {base}/{surface}'
        return ', '.join('/' + prefix + r + suffix + '/' for r in re.findall(r'/([^/]+)/', reading))
    return '/' + prefix + body + ending + suffix + '/'


def build_verb_payload(lexicon):
    entries = verbs()
    rows = []
    table = [line.split('\t') for line in TABLE.read_text(encoding='utf-8').splitlines() if line and not line.startswith('#')]
    assert {r[0] for r in table} == set(entries), 'Verb inventory changed: refresh and review the table.'
    for base, *columns in table:
        assert len(columns) == 4
        grouped = collections.OrderedDict()
        for tag, values in zip(TAGS, columns):
            for surface in values.split(','):
                assert re.fullmatch(r"[a-z]+(?:'[a-z]+)?(?: [a-z]+)*", surface), surface
                record = grouped.setdefault(surface, dict(word=surface, types=[], ipa=ipa(base, surface, tag, entries[base], lexicon)))
                record['types'] += [t for t in TYPES[tag] if t not in record['types']]
        for surface, record in grouped.items():
            if surface == base:
                continue  # A base sentence does not demonstrate the past-tense use.
            for sense in entries[base][1]:
                if re.search(r'(?<![a-z])' + re.escape(surface) + r'(?![a-z])', sense.get('example', '').lower()) and sense.get('exampleVi'):
                    record.update(example=sense['example'], exampleVi=sense['exampleVi'])
                    break
        rows.append(dict(word=base, forms=list(grouped.values())))
    return rows


def build_payload():
    lexicon = dict(line.split('\t', 1) for line in gzip.decompress(
        (ROOT / 'pronunciation/en-us.tsv.gzip').read_bytes()).decode().splitlines())
    rows = {r['word']: r for r in build_verb_payload(lexicon)}
    entries = nouns()
    table = [line.split('\t') for line in NOUN_TABLE.read_text(encoding='utf-8').splitlines()
             if line and not line.startswith('#')]
    assert len(table) == len(entries), 'Duplicate or missing noun review row'
    assert {r[0] for r in table} == set(entries), 'Noun inventory changed: review the table.'
    renames = {r['word']: r for r in read(NOUN_RENAMES)}
    for base, status, head_index, plurals in table:
        assert status in {'countable', 'invariant', 'mass', 'lexical_plural', 'existing_plural'}
        assert bool(plurals) == (status in {'countable', 'invariant'}), base
        if not plurals:
            continue
        row = rows.setdefault(base, dict(word=base, forms=[]))
        for surface in plurals.split(','):
            form = dict(word=surface, types=['plural'], ipa=noun_ipa(base, surface, int(head_index), entries[base], lexicon))
            for sense in entries[base][1]:
                if surface != base and re.search(r'(?<![a-z])' + re.escape(surface.lower()) + r'(?![a-z])', sense.get('example', '').lower()) and sense.get('exampleVi'):
                    form.update(example=sense['example'], exampleVi=sense['exampleVi'])
                    break
            if base in renames:
                form.update(renames[base]['plural'])
            old = next((f for f in row['forms'] if f['word'] == surface), None)
            if old:
                old['types'].append('plural')
                # A new verb sense can share a surface with an existing plural.
                # Keep its authored noun context when no verb context was found.
                if not old.get('example') and not old.get('exampleVi') and form.get('example'):
                    old.update(example=form['example'], exampleVi=form['exampleVi'])
                # Both readings are useful for noun/verb heteronyms.
                if old['ipa'] != form['ipa']:
                    old['ipa'] = ', '.join(dict.fromkeys(re.findall(r'/[^/]+/', old['ipa'] + ', ' + form['ipa'])))
            else:
                row['forms'].append(form)
        if base in renames:
            row.update({k: v for k, v in renames[base].items() if k not in {'word','plural','source'}})
    return [rows[k] for k in sorted(rows)]


def enrich(records, lookup):
    for word in tree_entries(records):
        forms = applicable_forms(word, lookup.get(word['word'], []))
        if forms:
            word['forms'] = forms
        else:
            word.pop('forms', None)
    return records


def apply_to_decks(payload):
    from phrase_bundles import place_phrases
    place_phrases()
    lookup = {w['word']: w['forms'] for w in payload}
    for path in sources():
        original = read(path)
        old_count = len(original)
        deck = enrich(normalize_nouns(original), lookup)
        assert len(deck) == old_count
        write(path, deck)
    from phrase_bundles import refresh_offline
    refresh_offline()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh-table', action='store_true')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if args.refresh_table:
        refresh_table(verbs())
    from phrase_bundles import place_phrases
    place_phrases()
    payload = build_payload()
    write(PAYLOAD, payload)
    if args.apply:
        apply_to_decks(payload)
        refresh_ielts(ROOT)
    print(f"PASS: {len(payload)} lemmas, {sum(len(w['forms']) for w in payload)} nested forms, no vocabulary rows added.")


if __name__ == '__main__':
    main()
