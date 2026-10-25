"""Apply authored bilingual examples by exact sense identity; never fill by guessing."""
import json
import subprocess
import sys
from pathlib import Path
from vocabulary_tree import entries as tree_entries
from ielts_bundles import source_decks, refresh as refresh_ielts, write as write_bundle_json

ROOT = Path(__file__).resolve().parents[1]
ROWS = '''absorb|The company will absorb the extra shipping costs.|Công ty sẽ gánh chịu chi phí vận chuyển phát sinh.
abstraction|The abstraction of water from the river is strictly controlled.|Việc lấy nước từ sông được kiểm soát nghiêm ngặt.
accelerate|The new policy will accelerate economic growth.|Chính sách mới sẽ thúc đẩy tăng trưởng kinh tế.
accessibility|The website needs better accessibility for blind users.|Trang web cần cải thiện khả năng sử dụng cho người khiếm thị.
accompany|She will accompany the singer on the piano.|Cô ấy sẽ đệm piano cho ca sĩ.
acknowledge|Please acknowledge receipt of this email.|Vui lòng xác nhận đã nhận được email này.
acquire|Patients can acquire an infection during treatment.|Bệnh nhân có thể bị nhiễm trùng trong quá trình điều trị.
acquisition|Language acquisition begins early in childhood.|Quá trình tiếp thu ngôn ngữ bắt đầu từ khi còn nhỏ.
adapt|They will adapt the novel for television.|Họ sẽ chuyển thể cuốn tiểu thuyết thành phim truyền hình.
adjust|Children need time to adjust to a new school.|Trẻ em cần thời gian để thích nghi với trường mới.
admire|We stopped to admire the view.|Chúng tôi dừng lại để ngắm cảnh.
admit|The museum will admit visitors until five.|Bảo tàng sẽ cho khách vào đến năm giờ.
adoption|They completed the adoption of a young child.|Họ đã hoàn tất việc nhận một đứa trẻ làm con nuôi.
advantage|This rule may advantage larger companies.|Quy định này có thể mang lại lợi thế cho các công ty lớn hơn.
advocate|She is an advocate for equal access to education.|Cô ấy là người công khai ủng hộ quyền tiếp cận giáo dục bình đẳng.
afford|The balcony will afford a clear view of the sea.|Ban công sẽ mang lại tầm nhìn thoáng ra biển.
agenda|He seems to have a hidden agenda.|Có vẻ anh ấy có một động cơ riêng được che giấu.
aggregate|The aggregate of these payments is ten thousand dollars.|Tổng các khoản thanh toán này là mười nghìn đô la.
aggressive|The doctor identified an aggressive form of cancer.|Bác sĩ xác định đây là một dạng ung thư phát triển dữ dội.
alignment|The parties announced their alignment on this issue.|Các bên công bố sự đồng thuận về vấn đề này.
allow|You should allow for delays when planning the journey.|Bạn nên tính đến việc chậm trễ khi lên kế hoạch chuyến đi.
allowance|She saves half of her weekly allowance.|Cô bé tiết kiệm một nửa tiền tiêu vặt hằng tuần.
alternative|He works at a clinic offering alternative medicine.|Anh ấy làm việc tại một phòng khám cung cấp các phương pháp y học thay thế.
analyse|Scientists will analyse the chemical composition of the sample.|Các nhà khoa học sẽ phân tích thành phần hóa học của mẫu.
announce|Please announce each guest as they enter.|Hãy xướng tên từng vị khách khi họ bước vào.
anticipate|We must anticipate problems and prepare a backup plan.|Chúng ta phải lường trước các vấn đề và chuẩn bị phương án dự phòng.
anxious|She is anxious to hear the results.|Cô ấy rất mong được nghe kết quả.
apparatus|The respiratory apparatus supplies oxygen to the body.|Hệ hô hấp cung cấp ôxy cho cơ thể.
apparent|His apparent confidence concealed his anxiety.|Sự tự tin bề ngoài của anh ấy che giấu nỗi lo lắng.
appendix|The surgeon removed her appendix.|Bác sĩ phẫu thuật đã cắt bỏ ruột thừa của cô ấy.
appliance|The dentist fitted a removable appliance.|Nha sĩ đã lắp một khí cụ có thể tháo rời.
apply|Apply the cream to clean skin.|Bôi kem lên vùng da sạch.
appraisal|The bank requested an appraisal of the house.|Ngân hàng yêu cầu định giá ngôi nhà.
appropriate|They tried to appropriate public funds for private use.|Họ tìm cách chiếm đoạt công quỹ để sử dụng riêng.
approve|I approve of your decision to continue studying.|Tôi tán thành quyết định tiếp tục học của bạn.
arbitrary|Let x be an arbitrary positive number.|Cho x là một số dương bất kỳ.
argue|These findings argue for a change in policy.|Những kết quả này cho thấy có cơ sở để thay đổi chính sách.
arrange|He will arrange the song for a string quartet.|Anh ấy sẽ chuyển soạn bài hát cho một nhóm tứ tấu đàn dây.
arrest|Early treatment can arrest the spread of the disease.|Điều trị sớm có thể chặn đứng sự lan rộng của bệnh.
articulate|She is an articulate speaker who explains ideas clearly.|Cô ấy là người diễn thuyết có khả năng trình bày ý tưởng rõ ràng.
artifact|The museum displays an ancient bronze artifact.|Bảo tàng trưng bày một hiện vật bằng đồng cổ.
artificial|His smile seemed artificial.|Nụ cười của anh ấy có vẻ giả tạo.
assertion|Her assertion that the plan would fail surprised us.|Lời khẳng định của cô ấy rằng kế hoạch sẽ thất bại khiến chúng tôi ngạc nhiên.
assist|The midfielder provided an assist for the winning goal.|Tiền vệ thực hiện một pha kiến tạo dẫn đến bàn thắng quyết định.
associate|A business associate introduced us.|Một cộng sự kinh doanh đã giới thiệu chúng tôi với nhau.
assume|She will assume the role of director next month.|Cô ấy sẽ đảm nhiệm vai trò giám đốc vào tháng tới.
assumption|His assumption of office marked a new beginning.|Việc ông ấy nhậm chức đánh dấu một khởi đầu mới.
assure|I can assure you that your data is safe.|Tôi có thể cam đoan để bạn yên tâm rằng dữ liệu của bạn được an toàn.
attach|Children can attach themselves to a favourite toy.|Trẻ em có thể trở nên gắn bó với một món đồ chơi yêu thích.
attachment|She feels a strong attachment to her hometown.|Cô ấy có tình cảm gắn bó sâu sắc với quê hương.
attempt|They will attempt to climb the mountain tomorrow.|Ngày mai họ sẽ cố gắng leo lên ngọn núi.
attitude|The pilot adjusted the aircraft's attitude.|Phi công điều chỉnh tư thế của máy bay.
attract|Magnets attract iron objects.|Nam châm hút các vật bằng sắt.
audience|The ambassador requested an audience with the king.|Đại sứ đề nghị được tiếp kiến nhà vua.
audit|Students may audit the course without earning credit.|Sinh viên có thể dự thính khóa học mà không nhận tín chỉ.
narrow|We need to narrow the search to three candidates.|Chúng ta cần thu hẹp việc tìm kiếm còn ba ứng viên.'''

def main():
    from everyday_extension import apply as apply_extension
    apply_extension()
    catalog_order = {path: {entry['url']: i for i, entry in enumerate(json.loads(path.read_text(encoding='utf-8'))['files'])}
                     for path in [ROOT/'catalog.json']}
    subprocess.run([sys.executable, str(ROOT / 'tools/build-b2-daily-work.py')], check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/build-daily-work-498.py')], check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/build-professional-1000.py')], check=True)
    subprocess.run([sys.executable, str(ROOT / 'tools/repair-reviewed-content.py')], check=True)
    from phrase_bundles import place_phrases
    place_phrases()
    source = ROOT / 'seed_words.json'
    seed = json.loads(source.read_text(encoding='utf-8'))
    # Freeze identity in a reviewable curation file rather than depend on array position.
    output = ROOT / 'tools/curated-sense-examples.json'
    if not output.exists():
        records = []
        for row in ROWS.splitlines():
            word, example, translation = row.split('|')
            entry = next(w for w in seed if w['word'] == word)
            sense = next(s for s in entry.get('senses', []) if not s.get('example'))
            records.append(dict(word=word, pos=sense['pos'], meaningVi=sense['meaningVi'], example=example, exampleVi=translation))
        output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    records = json.loads(output.read_text(encoding='utf-8')) + json.loads(
        (ROOT / 'tools/curated-awl-examples.json').read_text(encoding='utf-8')) + json.loads(
        (ROOT / 'tools/curated-b2-examples.json').read_text(encoding='utf-8')) + json.loads(
        (ROOT / 'tools/curated-core-examples.json').read_text(encoding='utf-8')) + json.loads(
        (ROOT / 'tools/curated-b2-daily-work-examples.json').read_text(encoding='utf-8')) + json.loads(
        (ROOT / 'tools/curated-daily-work-498-examples.json').read_text(encoding='utf-8')) + json.loads(
        (ROOT / 'tools/curated-professional-examples.json').read_text(encoding='utf-8')) + json.loads(
        (ROOT / 'tools/curated-reviewed-examples.json').read_text(encoding='utf-8')) + json.loads(
        (ROOT / 'tools/curated-basic-20-examples.json').read_text(encoding='utf-8')) + json.loads(
        (ROOT / 'tools/curated-basic-120-examples.json').read_text(encoding='utf-8')) + json.loads(
        (ROOT / 'tools/curated-everyday-500-examples.json').read_text(encoding='utf-8')) + json.loads(
        (ROOT / 'tools/curated-prepositions-examples.json').read_text(encoding='utf-8'))
    # Correct only known source definitions; repeated runs also accept the corrected identity.
    b2_path = ROOT / 'decks/b2-1000.json'
    b2 = json.loads(b2_path.read_text(encoding='utf-8'))
    for correction in json.loads((ROOT / 'tools/curated-b2-corrections.json').read_text(encoding='utf-8')):
        word = next(w for w in b2 if w['word'] == correction['word'])
        sense = next(s for s in word.get('senses', []) if
                     (s['pos'], s['meaningVi']) in [(correction['pos'], correction['meaningVi']),
                     (correction['newPos'], correction['newMeaningVi'])])
        sense.update(pos=correction['newPos'], meaningVi=correction['newMeaningVi'])
    b2_path.write_text(json.dumps(b2, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lookup = {(r['word'], r['pos'], r['meaningVi']): r for r in records}
    if len(lookup) != len(records):
        raise ValueError('Duplicate authored sense identity')
    files = [source] + source_decks(ROOT)
    corrections = {(r['word'], r['pos'], r['meaningVi']): r for r in json.loads(
        (ROOT / 'tools/curated-core-corrections.json').read_text(encoding='utf-8'))}
    def corrected_identity(word, sense):
        key = (word['word'], sense.get('pos', ''), sense['meaningVi'])
        correction = corrections.get(key)
        return (word['word'], correction['newPos'], correction['newMeaningVi']) if correction else key
    identities = {corrected_identity(w, s)
                  for file in files for w in tree_entries(json.loads(file.read_text(encoding='utf-8')))
                  for s in [w] + w.get('senses', [])}
    for key, record in lookup.items():
        if key not in identities or not record['example'].strip() or not record['exampleVi'].strip():
            raise ValueError(f'Invalid or stale authored example: {key}')
    changed = 0
    for file in files:
        original = file.read_text(encoding='utf-8')
        data = json.loads(original)
        dirty = False
        for word in tree_entries(data):
            for sense in [word] + word.get('senses', []):
                correction = corrections.get((word['word'], sense.get('pos', ''), sense['meaningVi']))
                if correction:
                    sense.update(pos=correction['newPos'], meaningVi=correction['newMeaningVi'])
                    dirty = True
                r = lookup.get((word['word'], sense.get('pos', ''), sense['meaningVi']))
                if r and (sense.get('example') != r['example'] or sense.get('exampleVi') != r['exampleVi']):
                    sense.update(example=r['example'], exampleVi=r['exampleVi'])
                    dirty = True
                    changed += 1
        if dirty:
            import re
            indent = len(re.search(r'^\[\n( +)\{', original).group(1))
            file.write_text(json.dumps(data, ensure_ascii=False, indent=indent) + '\n', encoding='utf-8')
    (ROOT / 'learning/sense-examples.json').write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # Earlier builders produce lexical data; restore the frozen forms and synonyms too.
    subprocess.run([sys.executable, str(ROOT/'tools/build-word-forms.py'), '--apply'], check=True)
    subprocess.run([sys.executable, str(ROOT/'tools/build-synonyms.py'), '--apply'], check=True)
    for path in [ROOT/'catalog.json']:
        catalog=json.loads(path.read_text(encoding='utf-8'))
        order = catalog_order[path]
        catalog['files'].sort(key=lambda entry:order.get(entry['url'],len(order)))
        write_bundle_json(path, catalog)
    refresh_ielts(ROOT)
    print(f'{len(records)} authored bilingual examples; {changed} matching senses updated.')

if __name__ == '__main__':
    main()
