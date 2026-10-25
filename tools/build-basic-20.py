"""Reproduce the 20 approved additions from locally authored bilingual content."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = 'basic-20.json'

def write(path, data):
    from phrase_bundles import retain_children
    retain_children(path, data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def build():
    rows = [
        ('book','noun','/bʊk/','sách','I borrowed two books from the library.','Tôi mượn hai cuốn sách từ thư viện.','education',[]),
        ('pass','verb','/pæs/','đi qua','We passed the station on our way home.','Chúng tôi đi qua nhà ga trên đường về nhà.','travel',['go past']),
        ('get','verb','/ɡet/','nhận được','I got your message this morning.','Tôi nhận được tin nhắn của bạn sáng nay.','daily',['receive']),
        ('take','verb','/teɪk/','lấy','She took a clean cup from the shelf.','Cô ấy lấy một chiếc cốc sạch từ trên kệ.','daily',[]),
        ('make','verb','/meɪk/','làm; tạo ra','He made a small table for the kitchen.','Anh ấy làm một chiếc bàn nhỏ cho nhà bếp.','daily',['create']),
        ('keep','verb','/kiːp/','giữ; giữ lại','I kept the receipt in my wallet.','Tôi giữ biên lai trong ví.','daily',['retain']),
        ('bring','verb','/brɪŋ/','mang đến','She brought some fruit to the meeting.','Cô ấy mang một ít trái cây đến cuộc họp.','daily',[]),
        ('choose','verb','/tʃuːz/','chọn','We chose a quiet room for the interview.','Chúng tôi chọn một phòng yên tĩnh để phỏng vấn.','daily',['select','pick']),
        ('remember','verb','/rɪˈmembər/','nhớ; nhớ lại','I remembered her name after a few minutes.','Tôi nhớ ra tên cô ấy sau vài phút.','daily',['recall']),
        ('forget','verb','/fərˈɡet/','quên','He forgot his password and had to reset it.','Anh ấy quên mật khẩu và phải đặt lại.','daily',[]),
        ('wallet','noun','/ˈwɑlɪt/','ví','I keep my cards in a small wallet.','Tôi để các thẻ của mình trong một chiếc ví nhỏ.','shopping',[]),
        ('receipt','noun','/rɪˈsiːt/','biên lai','Please keep your receipt in case you need a refund.','Hãy giữ biên lai phòng khi bạn cần hoàn tiền.','shopping',[]),
        ('refund','noun','/ˈriːfʌnd/','khoản tiền được hoàn lại','I received a full refund for the damaged charger.','Tôi nhận được khoản hoàn tiền đầy đủ cho bộ sạc bị hỏng.','shopping',['reimbursement']),
        ('charger','noun','/ˈtʃɑrdʒər/','bộ sạc','My phone charger is in the drawer.','Bộ sạc điện thoại của tôi ở trong ngăn kéo.','daily',[]),
        ('luggage','noun','/ˈlʌɡɪdʒ/','hành lý','We left our luggage at the hotel.','Chúng tôi để hành lý ở khách sạn.','travel',['baggage']),
        ('pharmacy','noun','/ˈfɑrməsi/','hiệu thuốc','There is a pharmacy next to the supermarket.','Có một hiệu thuốc cạnh siêu thị.','health',['drugstore']),
        ('follow up','verb','/ˈfɑloʊ ʌp/','theo dõi; xử lý tiếp','I followed up on the request with an email.','Tôi gửi một email để tiếp tục theo dõi yêu cầu.','work',[]),
        ('figure out','verb','/ˈfɪɡjər aʊt/','hiểu ra; tìm ra cách giải quyết','We figured out how to fix the problem.','Chúng tôi tìm ra cách khắc phục vấn đề.','work',['work out']),
        ('put off','verb','/pʊt ɔf/','trì hoãn','They put off the meeting until Friday.','Họ hoãn cuộc họp đến thứ Sáu.','work',['postpone','delay']),
        ('run out of','verb','/rʌn aʊt əv/','dùng hết; không còn','We ran out of milk this morning.','Sáng nay chúng tôi hết sữa.','daily',[]),
    ]
    result = [dict(word=w, pos=p, ipa=i, meaningVi=m, example=e, exampleVi=v,
        topic=t, tags=['basic-20',t], synonyms=s) for w,p,i,m,e,v,t,s in rows]
    by_word = {w['word']: w for w in result}
    senses = [
        ('book','verb','/bʊk/','đặt trước; đặt chỗ','We booked a room for two nights.','Chúng tôi đặt phòng cho hai đêm.'),
        ('pass','verb','/pæs/','vượt qua; đạt yêu cầu','She passed her driving test on the first attempt.','Cô ấy đỗ kỳ thi lái xe ngay lần đầu.'),
        ('pass','verb','/pæs/','đưa; chuyển cho người khác','Please pass me the salt.','Làm ơn đưa cho tôi lọ muối.'),
        ('get','verb','/ɡet/','lấy; có được','Can you get some bread on your way home?','Bạn có thể mua ít bánh mì trên đường về nhà không?'),
        ('get','verb','/ɡet/','trở nên','It gets cold here after sunset.','Ở đây trời trở lạnh sau khi mặt trời lặn.'),
        ('take','verb','/teɪk/','mang; đưa đến','I will take these documents to the office.','Tôi sẽ mang những tài liệu này đến văn phòng.'),
        ('take','verb','/teɪk/','mất một khoảng thời gian','The journey takes about an hour.','Chuyến đi mất khoảng một giờ.'),
        ('make','verb','/meɪk/','khiến; làm cho','That song always makes me smile.','Bài hát đó luôn khiến tôi mỉm cười.'),
        ('keep','verb','/kiːp/','tiếp tục làm','Keep practicing and your pronunciation will improve.','Hãy tiếp tục luyện tập, phát âm của bạn sẽ cải thiện.'),
        ('remember','verb','/rɪˈmembər/','nhớ làm điều gì','Remember to turn off the lights before you leave.','Nhớ tắt đèn trước khi bạn rời đi.'),
        ('forget','verb','/fərˈɡet/','quên làm điều gì','I forgot to send the attachment.','Tôi quên gửi tệp đính kèm.'),
        ('refund','verb','/rɪˈfʌnd/','hoàn tiền','The shop refunded the delivery fee.','Cửa hàng hoàn lại phí giao hàng.'),
    ]
    for word,pos,ipa,meaningVi,example,exampleVi in senses:
        by_word[word].setdefault('senses', []).append(dict(pos=pos,ipa=ipa,meaningVi=meaningVi,
            example=example,exampleVi=exampleVi))
    return result

if __name__ == '__main__':
    data = build()
    for path in [ROOT/'decks'/DECK]: write(path,data)
    pairs = [dict(word=w['word'], sourceGroup='basic-20',
        **{k:s[k] for k in ('pos','meaningVi','example','exampleVi')})
        for w in data for s in [w]+w.get('senses',[])]
    write(ROOT/'tools/curated-basic-20-examples.json',pairs)
    payload=ROOT/'learning/sense-examples.json'
    curated=['curated-sense-examples.json','curated-awl-examples.json','curated-b2-examples.json',
        'curated-core-examples.json','curated-b2-daily-work-examples.json','curated-daily-work-498-examples.json',
        'curated-professional-examples.json','curated-reviewed-examples.json','curated-basic-20-examples.json',
        'curated-basic-120-examples.json','curated-everyday-500-examples.json','curated-prepositions-examples.json']
    write(payload,sum((json.loads((ROOT/'tools'/name).read_text(encoding='utf-8')) for name in curated
        if (ROOT/'tools'/name).exists()),[]))
    for path in [ROOT/'catalog.json']:
        catalog=json.loads(path.read_text(encoding='utf-8'))
        catalog['files']=[f for f in catalog['files'] if f['url'] != 'decks/'+DECK]
        catalog['files'].insert(1,dict(title='Thông dụng · 20 từ bổ sung',
            description='20 mục thông dụng: book, pass, get, take… Gồm 19 từ mới và cách dùng động từ follow up, gộp vào follow-up nếu đã có. Có 12 nghĩa phụ, ví dụ Anh–Việt, dạng chia và đồng nghĩa phù hợp. Có sẵn offline trên Windows/Android.',
            url='decks/'+DECK,count=20))
        write(path,catalog)
    print('PASS: reproduced 20 approved entries and 32 bilingual meaning examples.')
