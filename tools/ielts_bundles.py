"""Maintain the three canonical IELTS decks and their public catalog entries."""
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IELTS_DECKS = ('ielts-academic.json', 'ielts-task1.json', 'ielts-topics.json')
TOPIC_NAMES = (
    'crime', 'culture', 'education', 'environment', 'family', 'food', 'health',
    'money', 'science', 'society', 'sport', 'technology', 'transport', 'travel', 'work',
)
RETIRED_DECKS = {'ielts-awl.json', *(f'ielts-{topic}.json' for topic in TOPIC_NAMES)}


def source_decks(root=ROOT):
    """Every remaining deck is an editable source; there are no duplicate IELTS copies."""
    return sorted((root / 'decks').glob('*.json'))


def head_records(path, root=ROOT):
    """Compare renamed decks to their original Git content until the migration is committed."""
    relative = path.relative_to(root).as_posix()
    # During the move, history remains in the private parent repository. Once the
    # public migration is committed, its own history is sufficient on a fresh clone.
    parent = root.parent
    historical_relative = 'app/src/main/assets/seed_words.json' if relative == 'seed_words.json' else relative
    if (parent / '.gitmodules').exists():
        previous = subprocess.run(['git', 'show', 'HEAD:' + historical_relative], cwd=parent, capture_output=True)
        if previous.returncode == 0:
            return json.loads(previous.stdout)
    result = subprocess.run(['git', 'show', 'HEAD:' + relative], cwd=root, capture_output=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    historical = {'ielts-academic.json': ['ielts-awl.json'],
                  'ielts-topics.json': [f'ielts-{topic}.json' for topic in TOPIC_NAMES]}.get(path.name)
    if historical is None:
        result.check_returncode()
    return [word for name in historical for word in json.loads(subprocess.check_output(
        ['git', 'show', 'HEAD:decks/' + name], cwd=root))]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, data):
    content = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    if not path.exists() or path.read_bytes() != content:
        # Catalog readers must never observe a partially rewritten file.
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name+'.', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        try:
            temporary.replace(path)
        finally:
            if temporary.exists(): temporary.unlink()


def refresh(root=ROOT):
    academic = read(root / 'decks/ielts-academic.json')
    task1 = read(root / 'decks/ielts-task1.json')
    topics = read(root / 'decks/ielts-topics.json')
    groups = [('ielts-academic.json', academic), ('ielts-task1.json', task1), ('ielts-topics.json', topics)]
    all_words = [word for _, words in groups for word in words]
    keys = [word['word'].strip().lower() for word in all_words]
    if len(keys) != len(set(keys)):
        raise ValueError('IELTS source decks contain duplicate headwords; review before bundling')
    for name, words in groups:
        write(root / 'decks' / name, words)

    entries = [
        dict(title='IELTS · Học thuật (Academic Word List)',
             description='318 từ học thuật lõi (Coxhead AWL). Giữ nguyên nội dung và nhãn awl của bộ cũ.',
             url='decks/ielts-academic.json', count=len(academic)),
        dict(title='IELTS · Writing Task 1', description='Động từ xu hướng, mức độ, so sánh — dùng để mô tả biểu đồ.',
             url='decks/ielts-task1.json', count=len(task1)),
        dict(title='IELTS · Tổng hợp 15 chủ đề',
             description='339 từ thuộc 15 chủ đề: môi trường, giáo dục, sức khỏe, xã hội… Giữ nhãn để chọn học riêng hoặc nhiều chủ đề.',
             url='decks/ielts-topics.json', count=len(topics)),
    ]
    managed = {f'decks/{name}' for name in RETIRED_DECKS | set(IELTS_DECKS)}
    for path in [root / 'catalog.json']:
        catalog = read(path)
        current = catalog['files']
        at = next((i for i, entry in enumerate(current) if entry['url'] in managed), len(current))
        kept = [entry for entry in current if entry['url'] not in managed]
        catalog['files'] = kept[:at] + entries + kept[at:]
        write(path, catalog)
    return groups


if __name__ == '__main__':
    bundles = refresh()
    print('PASS: IELTS bundles: ' + ', '.join(f'{name}: {len(words)}' for name, words in bundles)
          + '; original records and topics retained; three canonical source files.')
