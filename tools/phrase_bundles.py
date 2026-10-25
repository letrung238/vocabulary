"""Keep phrase ownership in canonical decks; derive the optional offline package."""
import copy
import runpy
from pathlib import Path
from ielts_bundles import read, write
from vocabulary_tree import entries

ROOT = Path(__file__).resolve().parents[1]
SUPPLEMENT = 'prepositions.json'


def sources(root=ROOT):
    return [root/'seed_words.json', *sorted((root/'decks').glob('*.json'))]


def retain_children(path, records):
    """Lexical builders replace parent fields, but do not own phrase definitions."""
    path = Path(path)
    if path.parent != ROOT/'decks' or path.name == SUPPLEMENT or not path.exists(): return
    previous = {w['word']:w.get('phrases', []) for w in read(path)}
    for word in records:
        if previous.get(word['word']) and 'phrases' not in word:
            word['phrases'] = copy.deepcopy(previous[word['word']])


def place_phrases(phrases=None, root=ROOT):
    """Restore after a deck rebuild, or distribute newly authored phrase definitions.

    Existing source records take priority over the generated offline package.
    Only the reviewed phrase names and the former copied anchors are relocated.
    """
    builder = runpy.run_path(str(root/'tools/build-prepositions.py'))
    authored = builder['build']()
    groups = builder['phrase_roots'](authored)
    new = {w['word']:w for w in builder['new_roots']()}
    paths = sources(root)
    decks = {path:read(path) for path in paths}
    supplement = root/'decks'/SUPPLEMENT
    known = {}
    for w in authored:
        known[w['word']] = w
    for data in decks.values():
        for w in entries(data): known[w['word']] = w
    selected = {w['word']:w for w in (phrases if phrases is not None else [known[w['word']] for w in authored])}
    assert set(selected) == {w['word'] for w in authored}
    owners = {}
    for path, data in decks.items():
        if path == supplement: continue
        for word in data:
            if word['word'] in groups: owners.setdefault(word['word'], word)
    assert set(groups) - set(owners) == set(new), 'Review missing or newly duplicated phrase parents'
    previous = {w['word']:w for w in decks.get(supplement, [])}
    decks[supplement] = [copy.deepcopy(previous.get(name, word)) for name, word in new.items()]
    decks[supplement].append(copy.deepcopy(selected['care of']))
    owners.update({w['word']:w for w in decks[supplement] if w['word'] in new})
    children = {name for names in groups.values() for name in names}
    for data in decks.values():
        for word in data:
            kept = [p for p in word.get('phrases', []) if p['word'] not in children]
            if kept: word['phrases'] = kept
            else: word.pop('phrases', None)
    for parent, names in groups.items():
        owners[parent].setdefault('phrases', []).extend(copy.deepcopy(selected[name]) for name in names)
    for path, data in decks.items(): write(path, data)
    return len(decks[supplement])


def refresh_offline(root=ROOT):
    """Build the optional phrase view in memory; never duplicate the canonical decks."""
    groups = read(root/'learning/phrase-roots.json')
    known = {}
    for path in sources(root):
        for word in read(path): known.setdefault(word['word'], word)
    bundle = [copy.deepcopy(known[name]) for name in groups]
    bundle.append(copy.deepcopy(known['care of']))
    assert len(bundle) == len(groups)+1 and sum(len(w.get('phrases', [])) for w in bundle) == sum(map(len, groups.values()))
    return bundle
