"""Traverse lexical entries while canonical files store phrases below their roots."""
def entries(words):
    for word in words:
        yield word
        yield from entries(word.get('phrases', []))


def owned_entries(path, words):
    """Every canonical record now owns its children; no copied anchors remain."""
    yield from entries(words)
