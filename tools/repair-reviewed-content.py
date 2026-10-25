"""Apply the reviewed corrections, retain exact preimages for installed-deck repairs.

The manifest is an explicit editorial decision, not a machine translation or a
heuristic synonym generator. Repeated runs must leave both content and preimages
unchanged. Native clients use the same preimages to preserve learner edits.
"""
import copy
import json
from pathlib import Path
from vocabulary_tree import entries as tree_entries
from ielts_bundles import source_decks, write as write_bundle_json

ROOT = Path(__file__).resolve().parents[1]
SEED = 'seed_words.json'
B2 = 'decks/b2-1000.json'
AWL = 'decks/ielts-academic.json'
IT = 'decks/it-advanced.json'
MANIFEST = ROOT / 'learning/content-corrections.json'


def read(file):
    return json.loads((ROOT / file).read_text(encoding='utf-8-sig'))


def write(file, data):
    path = ROOT / file
    text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if not path.exists() or path.read_text(encoding='utf-8-sig') != text:
        path.write_text(text, encoding='utf-8')


def identity(word, sense):
    return word, sense.get('pos', ''), sense['meaningVi']


def content(sense):
    return {key: sense.get(key, '') for key in ['pos', 'meaningVi', 'example', 'exampleVi', 'ipa']}


def main():
    if not (ROOT / IT).exists():
        write(IT, read('decks/it-advanced.json'))
    files = [SEED] + [p.relative_to(ROOT).as_posix() for p in source_decks(ROOT)]
    decks = {file: read(file) for file in files}
    originals = copy.deepcopy(decks)
    existing_manifest = read('learning/content-corrections.json') if MANIFEST.exists() else []
    for record in existing_manifest:
        if record['file'] == 'decks/it-advanced.json':
            record['file'] = IT
    decisions = {}

    def entry(file, word):
        return next(w for w in decks[file] if w['word'] == word)

    def edit(file, word, **fields):
        entry(file, word).update(fields)
        decisions.setdefault((file, word), 'Correct reviewed definition, pronunciation or bilingual context.')

    def example(word, en, vi, **fields):
        edit(B2, word, example=en, exampleVi=vi, **fields)

    def senses(file, word, values):
        edit(file, word, senses=values)

    def sense(pos, meaning, en, vi, ipa=''):
        result = dict(pos=pos, meaningVi=meaning, example=en, exampleVi=vi)
        if ipa:
            result['ipa'] = ipa
        return result

    # Primary sentences must illustrate the declared primary meaning and part of speech.
    example('waterproof', 'This waterproof bag kept my phone dry.', 'Chiếc túi chống nước này giữ điện thoại của tôi khô ráo.')
    example('hip', 'She hurt her hip while running.', 'Cô ấy bị đau ở hông khi đang chạy.')
    example('colon', 'Use a colon before the list.', 'Hãy dùng dấu hai chấm trước danh sách.')
    example('triangle', 'Draw an equilateral triangle on the whiteboard.', 'Hãy vẽ một tam giác đều lên bảng trắng.')
    example('worm', 'A worm wriggled through the damp soil.', 'Một con giun ngọ nguậy trong đất ẩm.')
    example('stake', 'Drive a wooden stake into the ground beside the plant.', 'Đóng một chiếc cọc gỗ xuống đất bên cạnh cây.')
    example('rim', 'The rim of the wheel was bent.', 'Vành bánh xe bị cong.')
    example('cuff', 'The shirt cuff was too tight.', 'Cổ tay áo quá chật.')
    example('rear', 'The rear tyre of the car is flat.', 'Lốp sau của chiếc xe bị xẹp.', ipa='/rɪə/')
    example('leash', 'Keep the dog on a leash outside.', 'Hãy giữ chó trên dây dắt khi ra ngoài.')
    example('alien', 'The alien applied for a residence permit.', 'Người ngoại quốc đó nộp đơn xin giấy phép cư trú.', meaningVi='người ngoại quốc (trong văn bản pháp lý)')
    example('deck', 'She shuffled the deck before the game.', 'Cô ấy xáo bộ bài trước khi bắt đầu trò chơi.')
    example('mate', "The ship's mate checked the cargo list.", 'Sĩ quan boong của tàu kiểm tra danh sách hàng hóa.')
    example('spur', 'The rider adjusted his spur before the ride.', 'Người cưỡi ngựa chỉnh lại chiếc đinh thúc ngựa trước khi lên đường.')
    example('snap', 'The dry branch can snap if you bend it.', 'Cành cây khô có thể gãy nếu bạn uốn nó.')
    example('unstable', 'The ladder is unstable on this floor.', 'Chiếc thang không vững trên sàn này.')
    example('hood', 'He lifted the hood to check the engine.', 'Anh ấy mở nắp ca pô để kiểm tra động cơ.', meaningVi='nắp ca pô (xe ô tô, tiếng Anh Mỹ)')
    example('inch', 'The board is one inch thick.', 'Tấm ván dày một inch.', meaningVi='inch (đơn vị độ dài bằng 2,54 cm)')
    example('distract', 'The loud music distracts him from his work.', 'Tiếng nhạc lớn khiến anh ấy mất tập trung khi làm việc.')
    example('scream', 'She screamed when she saw the spider.', 'Cô ấy hét lên khi nhìn thấy con nhện.')
    example('puzzle', 'The locked room was a puzzle that nobody could explain.', 'Căn phòng bị khóa là một điều bí ẩn mà không ai giải thích được.', meaningVi='điều bí ẩn; vấn đề khó hiểu')
    example('varied', 'We enjoyed a varied menu at the small cafe.', 'Chúng tôi thưởng thức thực đơn đa dạng tại quán cà phê nhỏ.')
    example('upper', 'She injured her upper arm during the match.', 'Cô ấy bị thương ở phần trên cánh tay trong trận đấu.')
    example('everlasting', 'The couple promised each other everlasting love.', 'Cặp đôi hứa dành cho nhau tình yêu vĩnh cửu.')
    example('severely', 'The bridge was severely damaged by the storm.', 'Cây cầu bị hư hại nghiêm trọng do cơn bão.')
    example('forum', 'Members share ideas on the online forum.', 'Các thành viên chia sẻ ý tưởng trên diễn đàn trực tuyến.')
    example('romance', 'The novel tells the story of a summer romance.', 'Cuốn tiểu thuyết kể về một chuyện tình mùa hè.', meaningVi='chuyện tình; mối quan hệ yêu đương')
    example('wit', 'She used her wit to solve the difficult problem.', 'Cô ấy dùng trí thông minh để giải quyết vấn đề khó.')
    example('mold', 'Green mold grew on the old bread.', 'Nấm mốc xanh mọc trên miếng bánh mì cũ.', meaningVi='nấm mốc (cách viết Mỹ; Anh: mould)')
    example('gay', 'He is openly gay.', 'Anh ấy công khai mình là người đồng tính.', meaningVi='đồng tính')
    example('limb', 'The injured bird could not move its left limb.', 'Con chim bị thương không thể cử động chi bên trái.', meaningVi='chi; tay hoặc chân')
    example('boiling', 'Boiling turns water into steam.', 'Sự sôi biến nước thành hơi nước.', meaningVi='sự sôi; việc đun sôi')
    example('booking', 'I made a booking for a room tomorrow.', 'Tôi đã đặt một phòng cho ngày mai.', meaningVi='sự đặt chỗ; đơn đặt chỗ')
    example('alert', 'The police alerted residents to the approaching storm.', 'Cảnh sát cảnh báo người dân về cơn bão đang đến gần.')
    example('backward', 'He stepped backward to let her pass.', 'Anh ấy bước lùi để cô ấy đi qua.', meaningVi='về phía sau; lùi lại')
    example('shrink', 'This wool sweater may shrink in hot water.', 'Chiếc áo len này có thể co lại trong nước nóng.')
    example('strip', 'Cut a narrow strip of paper.', 'Cắt một dải giấy hẹp.')
    example('surplus', 'The charity distributed surplus food to local families.', 'Tổ chức từ thiện phân phát thực phẩm dư thừa cho các gia đình địa phương.')
    example('solo', 'The pilot completed a solo flight across the sea.', 'Phi công hoàn thành chuyến bay một mình qua biển.', meaningVi='được thực hiện một mình')
    example('martial', 'The region remained under martial law for several months.', 'Vùng này nằm dưới thiết quân luật suốt vài tháng.', meaningVi='thuộc quân sự; thuộc chiến tranh')
    example('concentration', 'The salt concentration in this solution is low.', 'Nồng độ muối trong dung dịch này thấp.')
    example('corrupt', 'The corrupt official accepted bribes.', 'Viên chức tham nhũng đó nhận hối lộ.')
    example('regulation', 'The new regulation requires drivers to wear seat belts.', 'Quy định mới yêu cầu người lái xe thắt dây an toàn.', meaningVi='quy định; điều lệ')
    example('sometime', 'We should meet sometime next week.', 'Chúng ta nên gặp nhau vào lúc nào đó trong tuần tới.', meaningVi='vào lúc nào đó; một ngày nào đó', ipa='/ˈsʌm.taɪm/')
    example('polish', 'The wooden table has a beautiful polish.', 'Chiếc bàn gỗ có độ bóng đẹp.')
    example('multiply', 'Multiply the number of boxes by the price of each box.', 'Nhân số hộp với giá của mỗi hộp.')
    edit(B2, 'graphic', pos='noun')
    edit(B2, 'proposition', pos='noun', exampleVi='Cô ấy đọc to đề xuất đó cho cả lớp nghe.')
    edit(SEED, 'balance', meaningVi='sự cân bằng')

    # Replace repeated paraphrases with actual senses or usages; do not pad the deck.
    w = entry(B2, 'balloon')
    edit(B2, 'balloon', meaningVi='bóng bay; bong bóng', senses=[s for s in w['senses'] if 'khinh khí cầu' in s['meaningVi']])
    edit(B2, 'compression', senses=[s for s in entry(B2, 'compression')['senses'] if s['meaningVi'] == 'nén (dữ liệu)'],
         example='Compression of the spring stores energy.', exampleVi='Việc nén lò xo tích trữ năng lượng.')
    senses(B2, 'digest', [sense('verb', 'tiêu hóa thức ăn', 'The stomach helps digest food.', 'Dạ dày giúp tiêu hóa thức ăn.', '/daɪˈdʒest/')])
    senses(B2, 'oval', [sense('noun', 'sân hoặc đường đua hình bầu dục', 'The runners trained on the oval behind the school.', 'Các vận động viên tập trên đường đua hình bầu dục phía sau trường.')])
    senses(B2, 'slap', [sense('verb', 'tát; đánh bằng lòng bàn tay', 'She slapped him across the face.', 'Cô ấy tát vào mặt anh ta.')])
    senses(B2, 'martial', [sense('adjective', 'hiếu chiến; sẵn sàng chiến đấu', 'His martial spirit made him eager to fight.', 'Tinh thần hiếu chiến khiến anh ấy háo hức chiến đấu.')])
    senses(B2, 'scream', [s for s in entry(B2, 'scream')['senses'] if s['meaningVi'] == 'rít lên; kêu chói tai'])
    senses(B2, 'severely', [entry(B2, 'severely')['senses'][0]])
    senses(B2, 'upper', [s for s in entry(B2, 'upper')['senses'] if s['meaningVi'] == 'cao cấp; thượng cấp'])
    senses(B2, 'survival', [s for s in entry(B2, 'survival')['senses'] if s['meaningVi'] == 'vật còn sót lại'])
    edit(B2, 'survival', example='The rescue team found signs of survival after the storm.', exampleVi='Đội cứu hộ tìm thấy dấu hiệu có người sống sót sau cơn bão.')
    senses(B2, 'latter', [sense('adjective', 'thuộc giai đoạn cuối', 'In his latter years, he spent more time painting.', 'Trong những năm cuối đời, ông dành nhiều thời gian hơn cho hội họa.')])
    edit(B2, 'latter', meaningVi='thứ hai trong hai người hoặc vật vừa được nhắc đến')
    senses(B2, 'snap', [entry(B2, 'snap')['senses'][0], sense('verb', 'búng ngón tay', 'You can snap your fingers to the music.', 'Bạn có thể búng ngón tay theo nhịp nhạc.')])
    senses(B2, 'solo', [sense('noun', 'đoạn độc tấu; tiết mục độc diễn', 'Her piano solo impressed the audience.', 'Màn độc tấu piano của cô ấy gây ấn tượng với khán giả.')])
    senses(B2, 'gay', [sense('adjective', 'vui vẻ; rộn ràng (cách dùng cũ)', 'The old novel describes a gay evening of music and dancing.', 'Cuốn tiểu thuyết cũ miêu tả một buổi tối vui vẻ với âm nhạc và khiêu vũ.'),
                        sense('adjective', 'sặc sỡ; tươi sáng (cách dùng cũ)', 'The old poem describes gay ribbons decorating the room.', 'Bài thơ cũ miêu tả những dải ruy băng sặc sỡ trang trí căn phòng.')])
    entry(B2, 'wit')['senses'][0]['meaningVi'] = 'khả năng nói năng hóm hỉnh, nhanh trí'
    edit(B2, 'wit', senses=entry(B2, 'wit')['senses'])
    entry(B2, 'forum')['senses'][1]['meaningVi'] = 'quảng trường hoặc chợ công cộng ở La Mã cổ đại'
    edit(B2, 'forum', senses=entry(B2, 'forum')['senses'])
    senses(SEED, 'outlier', [sense('noun', 'người hoặc trường hợp khác biệt rõ rệt với số đông', 'As the only artist in a family of engineers, she was an outlier.', 'Là nghệ sĩ duy nhất trong gia đình toàn kỹ sư, cô ấy là một trường hợp khác biệt.')])
    senses('decks/ielts-topics.json', 'carbon', [sense('noun', 'giấy than; tờ giấy dùng để sao chép khi viết hoặc đánh máy', 'Put a carbon between the two sheets before typing.', 'Đặt một tờ giấy than giữa hai tờ giấy trước khi đánh máy.')])
    edit('decks/ielts-topics.json', 'carbon', meaningVi='cacbon; nguyên tố hóa học có ký hiệu C',
         example='Carbon is present in both diamond and graphite.', exampleVi='Cacbon có trong cả kim cương và than chì.')

    # Repair awkward gloss substitutions in the AWL primary translations.
    awl_vi = {
        'assign': 'Mỗi sinh viên được phân một người hướng dẫn trong tuần đầu.',
        'technical': 'Báo cáo quá chuyên sâu đối với độc giả phổ thông.',
        'create': 'Đề án tạo ra sáu nghìn việc làm trong hai năm.',
        'differentiate': 'Người đọc phải phân biệt ý kiến với sự kiện được thuật lại.',
        'infer': 'Ta chỉ có thể suy ra động cơ từ những gì người ta thực sự làm.',
        'immigrate': 'Ông bà của cô ấy nhập cư vào những năm 1950.',
        'incidence': 'Tỷ lệ mắc bệnh tiểu đường tăng gấp đôi trong hai mươi năm.',
        'intermediate': 'Khóa học phù hợp với người học ở trình độ trung cấp.',
        'internal': 'Một cuộc rà soát nội bộ không tìm thấy bằng chứng gian lận.',
        'item': 'Mỗi mục trong bảng hỏi đều được thử nghiệm trước.',
        'job': 'Tự động hóa sẽ định hình lại các công việc chứ không xóa bỏ chúng.',
        'label': 'Thực phẩm phải được dán nhãn ghi rõ nước xuất xứ.',
        'layer': 'Thủ tục hành chính khiến mỗi yêu cầu bị chậm trễ thêm một bước.',
        'levy': 'Một khoản phí nhỏ đối với túi nhựa đã làm giảm một nửa mức sử dụng.',
        'locate': 'Nhà máy được đặt cách xa mọi khu dân cư.',
        'manual': 'Các công việc lao động chân tay biến mất nhanh nhất ở miền bắc.',
        'medical': 'Việc đào tạo ngành y mất ít nhất sáu năm.',
        'mental': 'Các dịch vụ chăm sóc sức khỏe tinh thần đang quá tải.',
        'military': 'Chi tiêu quân sự vượt ngân sách giáo dục.',
        'minimum': 'Mức lương tối thiểu được nâng hai lần trong một năm.',
        'ministry': 'Bộ công bố số liệu nhập học vào mỗi mùa thu.',
        'notwithstanding': 'Bất chấp những hạn chế này, nghiên cứu vẫn có giá trị.',
        'complement': 'Bài học trực tuyến bổ sung cho việc dạy trên lớp chứ không thay thế nó.',
    }
    # The English sentence stays the source of truth; explicit edits below avoid guessing.
    for word, vi in awl_vi.items():
        if any(w['word'] == word for w in decks[AWL]):
            edit(AWL, word, exampleVi=vi)
    edit('decks/ielts-topics.json', 'community service',
         example='The court sentenced him to community service.', exampleVi='Tòa án tuyên phạt anh ấy lao động công ích.')

    # Sense-specific IPA: optional for words with identical readings, explicit for heteronyms.
    primary_ipa = {
        B2: {'content':'/kənˈtent/', 'defect':'/dɪˈfekt/', 'digest':'/ˈdaɪ.dʒest/',
             'duplicate':'/ˈdʒuː.plɪ.kət/', 'insult':'/ˈɪn.sʌlt/', 'relay':'/ˈriː.leɪ/',
             'ally':'/ˈæl.aɪ/', 'multiply':'/ˈmʌl.tɪ.plaɪ/', 'polish':'/ˈpɒl.ɪʃ/'},
        AWL: {'attribute':'/əˈtrɪb.juːt/', 'incline':'/ɪnˈklaɪn/', 'subordinate':'/səˈbɔː.dɪ.nət/', 'whereby':'/weəˈbaɪ/',
              'complement':'/ˈkɒm.plɪ.ment/'},
        'decks/ielts-topics.json': {'convict':'/kənˈvɪkt/', 'postgraduate':'/ˌpəʊstˈɡrædʒ.u.ət/',
            'graduate':'/ˈɡrædʒ.u.eɪt/', 'refugee':'/ˌref.juˈdʒiː/', 'jury':'/ˈdʒʊə.ri/', 'upgrade':'/ʌpˈɡreɪd/'},
    }
    for file, values in primary_ipa.items():
        for word, ipa in values.items():
            edit(file, word, ipa=ipa)
    secondary_ipa = {
        'advocate': {'noun':'/ˈæd.və.kət/'}, 'aggregate': {'noun':'/ˈæɡ.rɪ.ɡət/'},
        'appropriate': {'verb':'/əˈprəʊ.pri.eɪt/'}, 'articulate': {'adjective':'/ɑːˈtɪk.jə.lət/'},
        'associate': {'noun':'/əˈsəʊ.ʃi.ət/'}, 'conflict': {'verb':'/kənˈflɪkt/'},
        'contract': {'verb':'/kənˈtrækt/'}, 'contrast': {'verb':'/kənˈtrɑːst/'},
        'estimate': {'noun':'/ˈes.tɪ.mət/'}, 'extract': {'noun':'/ˈek.strækt/'},
        'frequent': {'verb':'/frɪˈkwent/'}, 'moderate': {'verb':'/ˈmɒd.ər.eɪt/'},
        'progress': {'verb':'/prəˈɡres/'}, 'refuse': {'noun':'/ˈref.juːs/'},
        'suspect': {'noun':'/ˈsʌs.pekt/'}, 'transfer': {'noun':'/ˈtræns.fɜː/'},
        'addict': {'verb':'/əˈdɪkt/'}, 'alternate': {'adjective':'/ɒlˈtɜː.nət/', 'noun':'/ˈɒl.tə.nət/'},
        'console': {'noun':'/ˈkɒn.səʊl/'}, 'content': {'noun':'/ˈkɒn.tent/'},
        'defect': {'noun':'/ˈdiː.fekt/'}, 'insult': {'verb':'/ɪnˈsʌlt/'},
        'rebel': {'verb':'/rɪˈbel/'}, 'relay': {'verb':'/ˌrɪˈleɪ/'},
        'resume': {'noun':'/ˈrez.juː.meɪ/'}, 'attribute': {'noun':'/ˈæt.rɪ.bjuːt/'},
        'conduct': {'noun':'/ˈkɒn.dʌkt/'}, 'convert': {'noun':'/ˈkɒn.vɜːt/'},
        'export': {'verb':'/ɪkˈspɔːt/'}, 'incline': {'noun':'/ˈɪn.klaɪn/'},
        'transport': {'verb':'/trænˈspɔːt/'}, 'convict': {'noun':'/ˈkɒn.vɪkt/'},
        'graduate': {'noun':'/ˈɡrædʒ.u.ət/'}, 'increase': {'noun':'/ˈɪn.kriːs/'},
        'protest': {'verb':'/prəˈtest/'},
        'combine': {'noun':'/ˈkɒm.baɪn/'}, 'decrease': {'noun':'/ˈdiː.kriːs/'},
        'delegate': {'noun':'/ˈdel.ɪ.ɡət/'}, 'deliberate': {'verb':'/dɪˈlɪb.ə.reɪt/'},
        'elaborate': {'verb':'/iˈlæb.ə.reɪt/'}, 'exploit': {'noun':'/ˈek.splɔɪt/'},
        'implement': {'noun':'/ˈɪm.plɪ.mənt/'}, 'interrupt': {'noun':'/ˈɪn.təˌrʌpt/'},
        'legitimate': {'verb':'/lɪˈdʒɪt.ɪˌmeɪt/'}, 'mediate': {'adjective':'/ˈmiː.di.ɪt/'},
        'offset': {'noun':'/ˈɒf.set/'}, 'prospect': {'verb':'/prəˈspekt/'},
        'reject': {'noun':'/ˈriː.dʒekt/'}, 'segment': {'verb':'/seɡˈment/'},
        'separate': {'noun':'/ˈsep.ər.ət/'}, 'ally': {'verb':'/əˈlaɪ/'},
        'compound': {'verb':'/kəmˈpaʊnd/'}, 'excuse': {'verb':'/ɪkˈskjuːz/'},
        'fragment': {'verb':'/fræɡˈment/'}, 'merchandise': {'verb':'/ˈmɜː.tʃən.daɪz/'},
        'multiply': {'adverb':'/ˈmʌl.tə.pli/'}, 'affect': {'noun':'/ˈæf.ekt/'},
        'approximate': {'verb':'/əˈprɒk.sɪ.meɪt/'}, 'complement': {'noun':'/ˈkɒm.plɪ.mənt/'},
        'construct': {'noun':'/ˈkɒn.strʌkt/'}, 'converse': {'verb':'/kənˈvɜːs/'},
        'coordinate': {'noun':'/kəʊˈɔː.dɪ.nət/'}, 'document': {'noun':'/ˈdɒk.jə.mənt/'},
        'insert': {'noun':'/ˈɪn.sɜːt/'}, 'overlap': {'noun':'/ˈəʊ.və.læp/'},
        'survey': {'verb':'/səˈveɪ/'}, 'upgrade': {'noun':'/ˈʌp.ɡreɪd/'},
    }
    for file in files:
        for w in decks[file]:
            variants = secondary_ipa.get(w['word'], {})
            for s in w.get('senses', []):
                if s['pos'] in variants:
                    s['ipa'] = variants[s['pos']]
                    decisions.setdefault((file, w['word']), 'Add the verified pronunciation of this secondary meaning.')

    # Ordinary and specialist senses that are actually distinct from the IT usage.
    additions = '''atomic|adjective|thuộc nguyên tử|Atomic energy can generate electricity.|Năng lượng nguyên tử có thể tạo ra điện.
bulkhead|noun|vách ngăn bên trong tàu hoặc máy bay|A steel bulkhead separates the ship's compartments.|Một vách ngăn thép chia các khoang của tàu.
circuit breaker|noun|cầu dao tự động ngắt điện khi có sự cố|The circuit breaker cut the power to the damaged cable.|Cầu dao tự động ngắt điện tới dây cáp bị hỏng.
closure|noun|sự đóng cửa hoặc chấm dứt hoạt động|The factory closure left many workers without jobs.|Việc đóng cửa nhà máy khiến nhiều công nhân mất việc.
cohesion|noun|sự đoàn kết, gắn bó của một nhóm|Shared goals strengthened cohesion within the team.|Mục tiêu chung củng cố sự đoàn kết trong đội.
cold start|noun|việc khởi động động cơ khi còn nguội|The engine struggled during a cold start on a winter morning.|Động cơ khó khởi động khi còn nguội vào một sáng mùa đông.
consensus|noun|sự nhất trí chung của một nhóm người|The committee reached a consensus on the new policy.|Ủy ban đạt được sự nhất trí về chính sách mới.
coupling|noun|bộ phận nối hai chi tiết cơ khí|The mechanic replaced the coupling between the two shafts.|Thợ máy thay khớp nối giữa hai trục.
drain|verb|rút hoặc làm chảy hết chất lỏng|Drain the water from the sink.|Xả hết nước trong bồn rửa.
drift|verb|trôi dạt theo gió hoặc dòng nước|The small boat began to drift away from the shore.|Chiếc thuyền nhỏ bắt đầu trôi xa bờ.
edge|noun|mép hoặc cạnh của một vật|Do not place the glass near the edge of the table.|Đừng đặt chiếc cốc gần mép bàn.
encapsulation|noun|sự bao bọc một chất trong lớp vỏ hoặc viên nang|Encapsulation protects the ingredient inside a thin coating.|Việc bao bọc bảo vệ thành phần bên trong một lớp phủ mỏng.
fixture|noun|vật được gắn cố định trong nhà hoặc công trình|The plumber installed a new bathroom fixture.|Thợ sửa ống nước lắp một thiết bị cố định mới trong phòng tắm.
handshake|noun|cái bắt tay khi chào hỏi hoặc thỏa thuận|They greeted each other with a firm handshake.|Họ chào nhau bằng một cái bắt tay chắc chắn.
heartbeat|noun|nhịp đập của tim|She could hear her own heartbeat in the quiet room.|Cô ấy nghe được nhịp tim của mình trong căn phòng yên tĩnh.
injection|noun|mũi tiêm; việc đưa thuốc vào cơ thể bằng kim tiêm|The nurse gave him an injection.|Y tá tiêm cho anh ấy một mũi.
jitter|verb|rung hoặc chuyển động nhanh, không đều|The loose wheel began to jitter on the rough road.|Bánh xe lỏng bắt đầu rung trên con đường gồ ghề.
lag|verb|tụt lại phía sau, tiến chậm hơn người khác|The tired runner began to lag behind the group.|Vận động viên mệt mỏi bắt đầu tụt lại phía sau nhóm.
monolith|noun|khối đá lớn nguyên khối|An ancient monolith stands beside the path.|Một khối đá cổ lớn đứng bên lối đi.
nonce|noun|thời điểm hiện tại (trong cụm for the nonce, cách dùng trang trọng hoặc cũ)|For the nonce, we will keep the current arrangement.|Tạm thời, chúng ta sẽ giữ cách sắp xếp hiện tại.
normalization|noun|việc đưa quan hệ hoặc tình trạng trở lại bình thường|The talks led to the normalization of relations between the countries.|Các cuộc đàm phán dẫn tới việc bình thường hóa quan hệ giữa các nước.
paging|noun|phân trang bộ nhớ; chuyển các trang dữ liệu giữa RAM và đĩa|Paging moves memory pages between RAM and disk.|Phân trang chuyển các trang bộ nhớ giữa RAM và đĩa.
partition|noun|vách ngăn chia một căn phòng|A wooden partition divides the office into two rooms.|Một vách ngăn gỗ chia văn phòng thành hai phòng.
polymorphism|noun|sự tồn tại nhiều dạng hình thái trong cùng một loài (sinh học)|The different shell colours illustrate polymorphism in this snail species.|Các màu vỏ khác nhau minh họa tính đa hình ở loài ốc này.
purge|verb|thanh trừng; loại bỏ người khỏi một tổ chức|The leader tried to purge his opponents from the party.|Người lãnh đạo tìm cách thanh trừng các đối thủ khỏi đảng.
quorum|noun|số thành viên tối thiểu cần có để cuộc họp ra quyết định hợp lệ|The committee cannot vote without a quorum.|Ủy ban không thể biểu quyết nếu chưa đủ số thành viên tối thiểu.
round robin|noun|giải đấu vòng tròn, mỗi người hoặc đội gặp tất cả đối thủ|The teams will compete in a round robin before the final.|Các đội sẽ thi đấu vòng tròn trước trận chung kết.
saga|noun|câu chuyện dài về nhiều sự kiện hoặc thế hệ|The novel is a family saga spanning three generations.|Cuốn tiểu thuyết là câu chuyện gia đình kéo dài qua ba thế hệ.
sanitization|noun|việc làm sạch, khử khuẩn|The kitchen closed briefly for sanitization.|Nhà bếp đóng cửa trong thời gian ngắn để làm sạch và khử khuẩn.
semaphore|noun|hệ thống truyền tín hiệu bằng vị trí của cờ hoặc cánh tay|The sailor sent a semaphore message using two flags.|Thủy thủ truyền một thông điệp bằng tín hiệu cờ với hai lá cờ.
side effect|noun|tác dụng phụ không mong muốn của thuốc hoặc phương pháp điều trị|Drowsiness is a possible side effect of this medicine.|Buồn ngủ là một tác dụng phụ có thể xảy ra của thuốc này.
sidecar|noun|thùng xe gắn bên cạnh xe máy|The passenger sat in the motorcycle's sidecar.|Hành khách ngồi trong thùng xe bên cạnh xe máy.
span|noun|khoảng thời gian kéo dài giữa hai mốc|The project was completed over a span of six months.|Dự án được hoàn thành trong khoảng thời gian sáu tháng.
starvation|noun|tình trạng thiếu thức ăn nghiêm trọng; sự chết đói|Food deliveries helped prevent starvation during the drought.|Các chuyến giao thực phẩm giúp ngăn nạn đói trong đợt hạn hán.
supply chain|noun|chuỗi các đơn vị và công đoạn đưa hàng hóa tới người tiêu dùng|A delay at the port disrupted the food supply chain.|Sự chậm trễ ở cảng làm gián đoạn chuỗi cung ứng thực phẩm.
throttling|noun|hành động bóp cổ, siết cổ|The detective investigated an attempted throttling.|Thám tử điều tra một vụ mưu toan bóp cổ.
toil|verb|làm việc nặng nhọc trong thời gian dài|They toil in the fields from dawn until sunset.|Họ làm việc vất vả ngoài đồng từ bình minh đến hoàng hôn.
warm-up|noun|bài khởi động trước khi vận động hoặc thi đấu|The players completed a short warm-up before the match.|Các cầu thủ thực hiện bài khởi động ngắn trước trận đấu.'''
    for row in additions.splitlines():
        word, pos, meaning, en, vi = row.split('|')
        w = entry(IT, word)
        new = sense(pos, meaning, en, vi)
        if not any(s['pos'] == pos and s['meaningVi'] == meaning for s in w.get('senses', [])):
            edit(IT, word, senses=w.get('senses', []) + [new])

    # Build exact before/after records once; preserve the historical preimage on later runs.
    previous = {(r['file'], r['word']): r for r in existing_manifest}
    manifest = []
    remapped = {}
    for (file, word), reason in sorted(decisions.items()):
        old = next(w for w in originals[file] if w['word'] == word)
        new = entry(file, word)
        historical = previous.get((file, word))
        if historical:
            old_main = historical['before']
            old_senses = historical['beforeSenses']
        else:
            old_main = content(old)
            old_senses = [content(s) for s in old.get('senses', [])]
        new_main = content(new)
        new_senses = [content(s) for s in new.get('senses', [])]
        if old_main == new_main and old_senses == new_senses:
            continue
        record = dict(file=file, word=word, reason=reason, before=old_main, after=new_main,
                      beforeSenses=old_senses, afterSenses=new_senses)
        manifest.append(record)
        # Retain authored records only if their sense still exists; migrate exact identities.
        for a, b in [(old_main, new_main)]:
            remapped[identity(word, a)] = identity(word, b)
    for record in previous.values():
        if (record['file'], record['word']) not in decisions:
            manifest.append(record)
    manifest.sort(key=lambda r: (r['file'], r['word']))

    # Frozen preimages from the first published professional deck enable safe upgrades.
    professional_file = 'decks/professional-reading-1000.json'
    professional_keys = {(professional_file, r['word']) for r in read('tools/professional-review-preimages.json')}
    manifest = [r for r in manifest if (r['file'], r['word']) not in professional_keys]
    for original in read('tools/professional-review-preimages.json'):
        word = entry(professional_file, original['word'])
        after, after_senses = content(word), [content(s) for s in word.get('senses', [])]
        if original['before'] != after or original['beforeSenses'] != after_senses:
            manifest.append(dict(original, after=after, afterSenses=after_senses))
    manifest.sort(key=lambda r: (r['file'], r['word']))

    for file, data in decks.items():
        write(file, data)
    write('learning/content-corrections.json', manifest)

    # Reconcile curation sources so the enrichment tool cannot restore reviewed errors.
    canonical = {identity(w['word'], s): s for data in decks.values() for w in tree_entries(data) for s in [w] + w.get('senses', [])}
    curated_files = ['curated-sense-examples.json', 'curated-awl-examples.json', 'curated-b2-examples.json', 'curated-core-examples.json', 'curated-b2-daily-work-examples.json', 'curated-daily-work-498-examples.json', 'curated-professional-examples.json']
    records = []
    for name in curated_files:
        updated = []
        for r in read('tools/' + name):
            key = identity(r['word'], r)
            new_key = remapped.get(key, key)
            target = canonical.get(new_key)
            if target is None:
                continue
            r.update(pos=new_key[1], meaningVi=new_key[2], example=target['example'], exampleVi=target['exampleVi'],
                     sourceGroup={'curated-sense-examples.json': 'seed', 'curated-awl-examples.json': 'awl',
                                  'curated-b2-examples.json': 'b2', 'curated-core-examples.json': 'core',
                                  'curated-b2-daily-work-examples.json': 'b2-daily-work',
                                  'curated-daily-work-498-examples.json': 'daily-work-498',
                                  'curated-professional-examples.json': 'professional-reading'}[name])
            if key != new_key:
                r.update(previousPos=key[1], previousMeaningVi=key[2])
            updated.append(r)
        write('tools/' + name, updated)
        records.extend(updated)
    supplements = sum((read('tools/' + name) for name in ['curated-basic-20-examples.json',
        'curated-basic-120-examples.json','curated-everyday-500-examples.json','curated-prepositions-examples.json']), [])
    authored = {identity(r['word'], r) for r in records + supplements}
    extra = []
    for patch in manifest:
        for s in [patch['after']] + patch['afterSenses']:
            key = identity(patch['word'], s)
            if key not in authored:
                extra.append(dict(word=patch['word'], sourceGroup='reviewed', **{k: s[k] for k in ['pos', 'meaningVi', 'example', 'exampleVi']}))
                authored.add(key)
    write('tools/curated-reviewed-examples.json', extra)
    write('learning/sense-examples.json', records + extra + supplements)

    multi = sum(bool(w.get('senses')) for w in decks[SEED])
    for file in ['catalog.json']:
        catalog = read(file)
        catalog['files'][0]['description'] = f"1.002 từ thông dụng và công việc/IT. {multi} từ có nghĩa phụ."
        if file == 'catalog.json' and not any(f['url'] == IT for f in catalog['files']):
            catalog['files'].append(dict(title='IT chuyên sâu', description='151 thuật ngữ chuyên sâu với ví dụ Anh–Việt và nghĩa khác khi có.', url=IT, count=len(decks[IT])))
        write(file, catalog)
    # Only real single-sense terms remain exceptions, now including the formerly omitted IT deck.
    missing = sorted({w['word'].lower() for file,data in decks.items()
        if Path(file).name not in {'basic-20.json','basic-120.json','everyday-500.json','prepositions.json'}
        for w in data if not w.get('senses')})
    exception_text = '# Reviewed exceptions without an independently authored secondary sense; never invent or repeat meanings.\n' + '\n'.join(missing) + '\n'
    (ROOT / 'tools/sense-exceptions.txt').write_text(exception_text, encoding='utf-8')
    print(f'{len(manifest)} reviewed word corrections; {len(extra)} additional authored contexts; '
          f'{sum(len(w.get("senses", [])) for data in decks.values() for w in data)} bilingual secondary senses.')


if __name__ == '__main__':
    main()
