"""Build the 120 approved everyday entries from local GPT-authored content."""
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECK = 'basic-120.json'

# word | POS | US IPA | Vietnamese sense | English example | translation | topic | synonyms
PRIMARY = """
know|verb|/noʊ/|biết|I knew the answer to the question.|Tôi biết câu trả lời cho câu hỏi đó.|daily|
think|verb|/θɪŋk/|nghĩ; suy nghĩ|We thought carefully before making a decision.|Chúng tôi suy nghĩ kỹ trước khi quyết định.|daily|consider
ask|verb|/æsk/|hỏi|She asked me a question about the timetable.|Cô ấy hỏi tôi một câu về bảng giờ chạy.|daily|inquire
tell|verb|/tel/|nói cho biết|He told me the new password.|Anh ấy cho tôi biết mật khẩu mới.|daily|inform
find|verb|/faɪnd/|tìm thấy|I found my keys under the sofa.|Tôi tìm thấy chìa khóa dưới ghế sofa.|daily|locate
give|verb|/ɡɪv/|cho; đưa|She gave me a clean towel.|Cô ấy đưa cho tôi một chiếc khăn sạch.|daily|
want|verb|/wɑnt/|muốn|I want a glass of water.|Tôi muốn một cốc nước.|daily|desire
need|verb|/niːd/|cần|We need more time to finish the work.|Chúng tôi cần thêm thời gian để hoàn thành công việc.|daily|require
use|verb|/juːz/|sử dụng|She used a map to find the station.|Cô ấy dùng bản đồ để tìm nhà ga.|daily|utilize
try|verb|/traɪ/|thử; cố gắng|We tried to fix the broken shelf.|Chúng tôi cố sửa chiếc kệ bị hỏng.|daily|attempt
leave|verb|/liːv/|rời đi|They left the office at six.|Họ rời văn phòng lúc sáu giờ.|daily|depart
buy|verb|/baɪ/|mua|I bought a new toothbrush yesterday.|Hôm qua tôi mua một chiếc bàn chải đánh răng mới.|shopping|purchase
sell|verb|/sel/|bán|They sold their old washing machine.|Họ bán chiếc máy giặt cũ.|shopping|
pay|verb|/peɪ/|trả tiền|I paid for the groceries with a card.|Tôi thanh toán tiền thực phẩm bằng thẻ.|shopping|
read|verb|/riːd/|đọc|She read the instructions before using the kettle.|Cô ấy đọc hướng dẫn trước khi dùng ấm đun nước.|education|
write|verb|/raɪt/|viết|He wrote a short message to his teacher.|Anh ấy viết một tin nhắn ngắn cho giáo viên.|education|
speak|verb|/spiːk/|nói|She spoke clearly during the meeting.|Cô ấy nói rõ ràng trong cuộc họp.|daily|talk
listen|verb|/ˈlɪsən/|lắng nghe|We listened to the weather report.|Chúng tôi nghe bản tin thời tiết.|daily|
help|verb|/help/|giúp đỡ|He helped me carry the suitcase.|Anh ấy giúp tôi mang va li.|daily|assist
work|verb|/wɜrk/|làm việc|She worked from home yesterday.|Hôm qua cô ấy làm việc ở nhà.|work|
kettle|noun|/ˈketəl/|ấm đun nước|Fill the kettle with fresh water.|Hãy đổ nước sạch vào ấm đun nước.|home|
saucepan|noun|/ˈsɔspæn/|nồi có cán|Heat the soup in a small saucepan.|Hãy hâm súp trong một chiếc nồi nhỏ có cán.|home|
drawer|noun|/drɔr/|ngăn kéo|The scissors are in the top drawer.|Kéo ở trong ngăn kéo trên cùng.|home|
toothpaste|noun|/ˈtuːθpeɪst/|kem đánh răng|We need to buy more toothpaste.|Chúng ta cần mua thêm kem đánh răng.|home|
toothbrush|noun|/ˈtuːθbrʌʃ/|bàn chải đánh răng|Keep your toothbrush clean and dry.|Hãy giữ bàn chải đánh răng sạch và khô.|home|
shampoo|noun|/ʃæmˈpuː/|dầu gội|This shampoo has a mild scent.|Loại dầu gội này có mùi thơm nhẹ.|home|
soap|noun|/soʊp/|xà phòng|Wash your hands with soap and water.|Hãy rửa tay bằng xà phòng và nước.|home|
towel|noun|/ˈtaʊəl/|khăn|Please bring a dry towel to the pool.|Hãy mang một chiếc khăn khô đến bể bơi.|home|
sink|noun|/sɪŋk/|bồn rửa|Leave the dirty cups in the sink.|Hãy để những chiếc cốc bẩn trong bồn rửa.|home|washbasin
sponge|noun|/spʌndʒ/|miếng bọt biển|Use a soft sponge to clean the pan.|Hãy dùng miếng bọt biển mềm để rửa chảo.|home|
detergent|noun|/dɪˈtɜrdʒənt/|chất giặt; chất tẩy rửa|Add a little detergent to the washing machine.|Hãy cho một ít chất giặt vào máy giặt.|home|
dishwasher|noun|/ˈdɪʃwɑʃər/|máy rửa bát|The dishwasher is full of clean plates.|Máy rửa bát chứa đầy đĩa sạch.|home|
washing machine|noun|/ˈwɑʃɪŋ məˌʃiːn/|máy giặt|Our washing machine is making a strange noise.|Máy giặt của chúng tôi phát ra tiếng lạ.|home|washer
freezer|noun|/ˈfriːzər/|tủ đông|Put the ice cream in the freezer.|Hãy cho kem vào tủ đông.|home|
vacuum cleaner|noun|/ˈvækjuəm ˌkliːnər/|máy hút bụi|I use a vacuum cleaner to clean the carpet.|Tôi dùng máy hút bụi để làm sạch thảm.|home|vacuum
broom|noun|/bruːm/|chổi|Use a broom to sweep the kitchen floor.|Hãy dùng chổi để quét sàn bếp.|home|
mop|noun|/mɑp/|cây lau nhà|Rinse the mop after cleaning the floor.|Hãy giặt cây lau nhà sau khi lau sàn.|home|
shelf|noun|/ʃelf/|kệ|Put the books on the top shelf.|Hãy đặt sách lên kệ trên cùng.|home|
cupboard|noun|/ˈkʌbərd/|tủ đựng đồ|The cups are in the kitchen cupboard.|Cốc ở trong tủ bếp.|home|cabinet
curtain|noun|/ˈkɜrtən/|rèm cửa|Close the curtain before going to bed.|Hãy kéo rèm trước khi đi ngủ.|home|drape
bread|noun|/bred/|bánh mì|I bought some fresh bread for breakfast.|Tôi mua ít bánh mì mới làm cho bữa sáng.|food|
rice|noun|/raɪs/|gạo|Store the rice in a dry container.|Hãy bảo quản gạo trong hộp khô.|food|
pasta|noun|/ˈpɑstə/|mì kiểu Ý|Cook the pasta in boiling water.|Hãy nấu mì Ý trong nước sôi.|food|
potato|noun|/pəˈteɪtoʊ/|khoai tây|She peeled the potatoes before cooking them.|Cô ấy gọt khoai tây trước khi nấu.|food|
tomato|noun|/təˈmeɪtoʊ/|cà chua|Slice a tomato for the sandwich.|Hãy thái một quả cà chua để làm bánh mì kẹp.|food|
onion|noun|/ˈʌnjən/|hành tây|Chop the onion into small pieces.|Hãy thái hành tây thành những miếng nhỏ.|food|
garlic|noun|/ˈɡɑrlɪk/|tỏi|Add a little garlic to the sauce.|Hãy cho một ít tỏi vào nước sốt.|food|
carrot|noun|/ˈkærət/|cà rốt|Wash the carrots before making the soup.|Hãy rửa cà rốt trước khi nấu súp.|food|
lettuce|noun|/ˈletɪs/|rau xà lách|Put some lettuce in the sandwich.|Hãy cho một ít rau xà lách vào bánh mì kẹp.|food|
cucumber|noun|/ˈkjuːkʌmbər/|dưa chuột|Cut the cucumber into thin slices.|Hãy thái dưa chuột thành những lát mỏng.|food|
beef|noun|/biːf/|thịt bò|We cooked beef with onions for dinner.|Chúng tôi nấu thịt bò với hành tây cho bữa tối.|food|
pork|noun|/pɔrk/|thịt lợn|The restaurant serves pork with steamed rice.|Nhà hàng phục vụ thịt lợn với cơm.|food|
chicken|noun|/ˈtʃɪkən/|gà|The farmer keeps chickens behind the house.|Người nông dân nuôi gà phía sau nhà.|food|
fish|noun|/fɪʃ/|cá|We saw several fish in the clear water.|Chúng tôi nhìn thấy vài con cá trong làn nước trong.|food|
egg|noun|/eɡ/|trứng|She fried an egg for breakfast.|Cô ấy chiên một quả trứng cho bữa sáng.|food|
cheese|noun|/tʃiːz/|phô mai|Add some cheese to the pasta.|Hãy cho một ít phô mai vào mì Ý.|food|
butter|noun|/ˈbʌtər/|bơ từ sữa|Spread a little butter on the bread.|Hãy phết một ít bơ lên bánh mì.|food|
yogurt|noun|/ˈjoʊɡərt/|sữa chua|I eat plain yogurt with fruit.|Tôi ăn sữa chua không thêm vị cùng trái cây.|food|yoghurt
milk|noun|/mɪlk/|sữa|Keep the milk in the refrigerator.|Hãy để sữa trong tủ lạnh.|food|
flour|noun|/ˈflaʊər/|bột mì|Mix the flour with a little water.|Hãy trộn bột mì với một ít nước.|food|
shirt|noun|/ʃɜrt/|áo sơ mi|He wore a clean shirt to the interview.|Anh ấy mặc áo sơ mi sạch đến buổi phỏng vấn.|clothing|
sweater|noun|/ˈswetər/|áo len|Bring a sweater because it gets cold at night.|Hãy mang áo len vì ban đêm trời trở lạnh.|clothing|jumper
jacket|noun|/ˈdʒækɪt/|áo khoác ngắn|She put on a jacket before going outside.|Cô ấy mặc áo khoác trước khi ra ngoài.|clothing|
coat|noun|/koʊt/|áo khoác ngoài|Hang your coat by the door.|Hãy treo áo khoác của bạn cạnh cửa.|clothing|
jeans|noun|/dʒiːnz/|quần bò|These jeans are comfortable and easy to wash.|Chiếc quần bò này thoải mái và dễ giặt.|clothing|denims
shorts|noun|/ʃɔrts/|quần đùi|He wore shorts on the hot afternoon.|Anh ấy mặc quần đùi vào buổi chiều nóng nực.|clothing|
skirt|noun|/skɜrt/|chân váy|She chose a blue skirt for the party.|Cô ấy chọn một chiếc chân váy màu xanh cho bữa tiệc.|clothing|
dress|noun|/dres/|váy liền|She bought a simple dress for the wedding.|Cô ấy mua một chiếc váy liền đơn giản để dự đám cưới.|clothing|
sock|noun|/sɑk/|tất|I found one sock under the bed.|Tôi tìm thấy một chiếc tất dưới giường.|clothing|
shoe|noun|/ʃuː/|giày|There is a small stone in my shoe.|Có một viên đá nhỏ trong giày của tôi.|clothing|
boot|noun|/buːt/|giày bốt|These boots keep my feet dry in the rain.|Đôi bốt này giữ chân tôi khô khi trời mưa.|clothing|
hat|noun|/hæt/|mũ|Wear a hat when you go out in the sun.|Hãy đội mũ khi ra ngoài trời nắng.|clothing|
scarf|noun|/skɑrf/|khăn quàng|She wrapped a scarf around her neck.|Cô ấy quàng một chiếc khăn quanh cổ.|clothing|
glove|noun|/ɡlʌv/|găng tay|Wear a glove to protect your hand.|Hãy đeo găng tay để bảo vệ bàn tay.|clothing|
belt|noun|/belt/|thắt lưng|This belt is too long for me.|Chiếc thắt lưng này quá dài với tôi.|clothing|
underwear|noun|/ˈʌndərwer/|đồ lót|I packed clean underwear for the trip.|Tôi chuẩn bị đồ lót sạch cho chuyến đi.|clothing|
pajamas|noun|/pəˈdʒɑməz/|đồ ngủ|He changed into his pajamas before bed.|Anh ấy thay đồ ngủ trước khi đi ngủ.|clothing|pyjamas
swimsuit|noun|/ˈswɪmsuːt/|đồ bơi|Bring a swimsuit if you want to use the pool.|Hãy mang đồ bơi nếu bạn muốn dùng bể bơi.|clothing|bathing suit
zipper|noun|/ˈzɪpər/|khóa kéo|The zipper on my backpack is broken.|Khóa kéo trên ba lô của tôi bị hỏng.|clothing|zip
pocket|noun|/ˈpɑkɪt/|túi áo; túi quần|He put the receipt in his pocket.|Anh ấy bỏ biên lai vào túi.|clothing|
head|noun|/hed/|đầu|Wear a helmet to protect your head.|Hãy đội mũ bảo hiểm để bảo vệ đầu.|health|
face|noun|/feɪs/|khuôn mặt|She washed her face with cool water.|Cô ấy rửa mặt bằng nước mát.|health|
eye|noun|/aɪ/|mắt|A little dust got into my eye.|Một ít bụi bay vào mắt tôi.|health|
ear|noun|/ɪr/|tai|The doctor examined my ear.|Bác sĩ kiểm tra tai của tôi.|health|
nose|noun|/noʊz/|mũi|Cover your nose and mouth when you sneeze.|Hãy che mũi và miệng khi hắt hơi.|health|
mouth|noun|/maʊθ/|miệng|Open your mouth so the dentist can check your teeth.|Hãy mở miệng để nha sĩ kiểm tra răng.|health|
tooth|noun|/tuːθ/|răng|I brush each tooth carefully.|Tôi chải từng chiếc răng cẩn thận.|health|
neck|noun|/nek/|cổ|My neck hurts after sitting at the computer all day.|Cổ tôi đau sau khi ngồi máy tính cả ngày.|health|
shoulder|noun|/ˈʃoʊldər/|vai|She carried the bag on her shoulder.|Cô ấy đeo túi trên vai.|health|
arm|noun|/ɑrm/|cánh tay|He raised his arm to ask a question.|Anh ấy giơ tay để hỏi.|health|
hand|noun|/hænd/|bàn tay|Wash each hand thoroughly before eating.|Hãy rửa kỹ từng bàn tay trước khi ăn.|health|
finger|noun|/ˈfɪŋɡər/|ngón tay|She pointed at the map with her finger.|Cô ấy dùng ngón tay chỉ vào bản đồ.|health|
stomach|noun|/ˈstʌmək/|dạ dày|My stomach feels uncomfortable after a large meal.|Dạ dày tôi khó chịu sau một bữa ăn lớn.|health|
leg|noun|/leɡ/|chân|He injured his leg while playing football.|Anh ấy bị thương ở chân khi chơi bóng đá.|health|
knee|noun|/niː/|đầu gối|She bent her knee slowly.|Cô ấy gập đầu gối từ từ.|health|
foot|noun|/fʊt/|bàn chân|There is a blister on my left foot.|Có một vết phồng rộp ở bàn chân trái của tôi.|health|
brain|noun|/breɪn/|não|Sleep helps the brain recover after a busy day.|Giấc ngủ giúp não phục hồi sau một ngày bận rộn.|health|
headache|noun|/ˈhedeɪk/|đau đầu|I have a headache and need some rest.|Tôi bị đau đầu và cần nghỉ ngơi.|health|
bandage|noun|/ˈbændɪdʒ/|băng dùng băng bó|The nurse put a bandage around his wrist.|Y tá quấn băng quanh cổ tay anh ấy.|health|
painkiller|noun|/ˈpeɪnˌkɪlər/|thuốc giảm đau|The pharmacist explained how to use the painkiller.|Dược sĩ giải thích cách dùng thuốc giảm đau.|health|analgesic
bus stop|noun|/ˈbʌs stɑp/|điểm dừng xe buýt|The bus stop is across the street.|Điểm dừng xe buýt ở bên kia đường.|travel|
train station|noun|/ˈtreɪn ˌsteɪʃən/|ga tàu|We met outside the train station.|Chúng tôi gặp nhau bên ngoài ga tàu.|travel|railway station
timetable|noun|/ˈtaɪmˌteɪbəl/|bảng giờ chạy; thời gian biểu|Check the timetable before leaving home.|Hãy kiểm tra bảng giờ chạy trước khi rời nhà.|travel|schedule
boarding pass|noun|/ˈbɔrdɪŋ pæs/|thẻ lên máy bay|Keep your boarding pass ready at the gate.|Hãy chuẩn bị sẵn thẻ lên máy bay khi đến cửa ra máy bay.|travel|boarding card
departure gate|noun|/dɪˈpɑrtʃər ɡeɪt/|cửa ra máy bay|Our departure gate has changed.|Cửa ra máy bay của chúng tôi đã thay đổi.|travel|boarding gate
baggage claim|noun|/ˈbæɡɪdʒ kleɪm/|khu nhận hành lý|Follow the signs to baggage claim.|Hãy đi theo biển chỉ dẫn đến khu nhận hành lý.|travel|baggage reclaim
seat belt|noun|/ˈsiːt belt/|dây an toàn|Fasten your seat belt before the car moves.|Hãy thắt dây an toàn trước khi xe chạy.|travel|safety belt
traffic light|noun|/ˈtræfɪk laɪt/|đèn giao thông|Stop when the traffic light turns red.|Hãy dừng lại khi đèn giao thông chuyển đỏ.|travel|traffic signal
crosswalk|noun|/ˈkrɔsˌwɔk/|vạch sang đường|Use the crosswalk to cross the road safely.|Hãy dùng vạch sang đường để qua đường an toàn.|travel|pedestrian crossing
roundabout|noun|/ˈraʊndəˌbaʊt/|vòng xuyến|Take the second exit at the roundabout.|Hãy đi theo lối ra thứ hai tại vòng xuyến.|travel|traffic circle
parking lot|noun|/ˈpɑrkɪŋ lɑt/|bãi đỗ xe|We left the car in the parking lot.|Chúng tôi để xe trong bãi đỗ xe.|travel|car park
parking meter|noun|/ˈpɑrkɪŋ ˌmiːtər/|máy tính phí đỗ xe|Pay at the parking meter before leaving your car.|Hãy trả phí ở máy tính phí đỗ xe trước khi rời xe.|travel|
speed limit|noun|/ˈspiːd ˌlɪmɪt/|giới hạn tốc độ|The speed limit on this road is fifty kilometers per hour.|Giới hạn tốc độ trên đường này là năm mươi ki lô mét mỗi giờ.|travel|
traffic jam|noun|/ˈtræfɪk dʒæm/|ùn tắc giao thông|We were late because of a traffic jam.|Chúng tôi đến muộn vì ùn tắc giao thông.|travel|
detour|noun|/ˈdiːtʊr/|đường vòng|We took a detour because the bridge was closed.|Chúng tôi đi đường vòng vì cầu bị đóng.|travel|diversion
shortcut|noun|/ˈʃɔrtˌkʌt/|đường tắt|This path is a shortcut to the station.|Lối này là đường tắt đến nhà ga.|travel|
suitcase|noun|/ˈsuːtˌkeɪs/|va li|My suitcase is too heavy to carry upstairs.|Va li của tôi quá nặng để mang lên cầu thang.|travel|
backpack|noun|/ˈbækˌpæk/|ba lô|I put a bottle of water in my backpack.|Tôi bỏ một chai nước vào ba lô.|travel|rucksack
umbrella|noun|/ʌmˈbrelə/|ô; dù|Take an umbrella because it may rain.|Hãy mang ô vì trời có thể mưa.|travel|
travel adapter|noun|/ˈtrævəl əˌdæptər/|đầu chuyển ổ cắm khi đi du lịch|Bring a travel adapter to charge your phone abroad.|Hãy mang đầu chuyển ổ cắm để sạc điện thoại khi ở nước ngoài.|travel|
"""

# Common secondary senses, with their own pronunciation and bilingual context.
SECONDARY = """
know|verb|/noʊ/|quen biết|I have known her since we were children.|Tôi quen cô ấy từ khi chúng tôi còn nhỏ.
think|verb|/θɪŋk/|cho rằng|I think this jacket is too small.|Tôi cho rằng chiếc áo khoác này quá nhỏ.
ask|verb|/æsk/|yêu cầu; đề nghị|He asked me to close the window.|Anh ấy nhờ tôi đóng cửa sổ.
tell|verb|/tel/|kể|She told the children a story.|Cô ấy kể cho bọn trẻ một câu chuyện.
find|verb|/faɪnd/|nhận thấy|I find this book useful for learning English.|Tôi thấy cuốn sách này hữu ích cho việc học tiếng Anh.
give|verb|/ɡɪv/|tặng|We gave him a scarf for his birthday.|Chúng tôi tặng anh ấy một chiếc khăn quàng vào dịp sinh nhật.
need|noun|/niːd/|nhu cầu|The survey identified a need for better transport.|Khảo sát xác định nhu cầu cải thiện giao thông.
use|noun|/juːs/|công dụng|This tool has several useful uses.|Dụng cụ này có vài công dụng hữu ích.
try|noun|/traɪ/|lần thử|It took three tries to open the jar.|Phải thử ba lần mới mở được chiếc lọ.
leave|verb|/liːv/|để lại|I left my umbrella on the bus.|Tôi để quên ô trên xe buýt.
leave|noun|/liːv/|thời gian nghỉ phép|She is on annual leave this week.|Tuần này cô ấy đang nghỉ phép năm.
pay|noun|/peɪ/|tiền công; tiền lương|The new job offers better pay.|Công việc mới có mức lương tốt hơn.
speak|verb|/spiːk/|nói một ngôn ngữ|He speaks English and Vietnamese.|Anh ấy nói tiếng Anh và tiếng Việt.
help|noun|/help/|sự giúp đỡ|Thank you for your help with the move.|Cảm ơn bạn đã giúp đỡ việc chuyển nhà.
work|noun|/wɜrk/|công việc; việc phải làm|I have a lot of work to finish today.|Hôm nay tôi có nhiều công việc cần hoàn thành.
work|verb|/wɜrk/|hoạt động; có tác dụng|The charger works well with my phone.|Bộ sạc hoạt động tốt với điện thoại của tôi.
rice|noun|/raɪs/|cơm|We had rice and chicken for lunch.|Chúng tôi ăn cơm với thịt gà vào bữa trưa.
chicken|noun|/ˈtʃɪkən/|thịt gà|Cook the chicken thoroughly before serving it.|Hãy nấu thịt gà chín kỹ trước khi phục vụ.
fish|noun|/fɪʃ/|thịt cá dùng làm thực phẩm|We had grilled fish for dinner.|Chúng tôi ăn cá nướng vào bữa tối.
fish|verb|/fɪʃ/|câu cá; đánh bắt cá|They fished in the river all morning.|Họ câu cá ở sông suốt buổi sáng.
coat|noun|/koʊt/|lớp phủ|The wall needs another coat of paint.|Bức tường cần thêm một lớp sơn.
head|noun|/hed/|người đứng đầu|The head of the team welcomed the new members.|Người đứng đầu nhóm chào đón các thành viên mới.
head|verb|/hed/|đứng đầu; lãnh đạo|She heads a team of five designers.|Cô ấy đứng đầu một nhóm gồm năm nhà thiết kế.
face|verb|/feɪs/|đối mặt|We faced several problems during the move.|Chúng tôi đối mặt với vài vấn đề trong lúc chuyển nhà.
hand|verb|/hænd/|đưa; trao|She handed me the boarding pass.|Cô ấy đưa cho tôi thẻ lên máy bay.
stomach|noun|/ˈstʌmək/|bụng|The baby was lying on her stomach.|Em bé đang nằm sấp.
foot|noun|/fʊt/|đơn vị chiều dài foot|The shelf is three feet long.|Chiếc kệ dài ba foot.
brain|noun|/breɪn/|trí óc; khả năng suy nghĩ|Use your brain to solve the puzzle.|Hãy dùng trí óc để giải câu đố.
headache|noun|/ˈhedeɪk/|vấn đề gây phiền toái|The repeated delays are a headache for the team.|Việc chậm trễ lặp lại gây phiền toái cho cả nhóm.
shortcut|noun|/ˈʃɔrtˌkʌt/|phím tắt|Use this keyboard shortcut to save the file.|Hãy dùng phím tắt này để lưu tệp.
"""

VERBS = """
know|knows|knowing|knew|known
think|thinks|thinking|thought|thought
ask|asks|asking|asked|asked
tell|tells|telling|told|told
find|finds|finding|found|found
give|gives|giving|gave|given
want|wants|wanting|wanted|wanted
need|needs|needing|needed|needed
use|uses|using|used|used
try|tries|trying|tried|tried
leave|leaves|leaving|left|left
buy|buys|buying|bought|bought
sell|sells|selling|sold|sold
pay|pays|paying|paid|paid
read|reads|reading|read|read
write|writes|writing|wrote|written
speak|speaks|speaking|spoke|spoken
listen|listens|listening|listened|listened
help|helps|helping|helped|helped
work|works|working|worked|worked
fish|fishes|fishing|fished|fished
head|heads|heading|headed|headed
face|faces|facing|faced|faced
hand|hands|handing|handed|handed
"""
MASS = {'toothpaste','shampoo','soap','detergent','bread','rice','pasta','garlic','lettuce',
    'beef','pork','cheese','butter','yogurt','milk','flour','underwear','baggage claim','leave','pay','help','work'}
LEXICAL_PLURAL = {'jeans','shorts','pajamas'}
IRREGULAR_PLURAL = {'shelf':'shelves','scarf':'scarves,scarfs','tooth':'teeth','foot':'feet'}

def lines(value): return [line.split('|') for line in value.strip().splitlines()]
def write(path,data):
    from phrase_bundles import retain_children
    retain_children(path, data)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def build():
    deck=[]
    for word,pos,ipa,meaningVi,example,exampleVi,topic,synonyms in lines(PRIMARY):
        deck.append(dict(word=word,pos=pos,ipa=ipa,meaningVi=meaningVi,example=example,
            exampleVi=exampleVi,topic=topic,tags=['basic-120',topic],synonyms=synonyms.split(';') if synonyms else []))
    by_word={w['word']:w for w in deck}
    for word,pos,ipa,meaningVi,example,exampleVi in lines(SECONDARY):
        by_word[word].setdefault('senses',[]).append(dict(pos=pos,ipa=ipa,meaningVi=meaningVi,example=example,exampleVi=exampleVi))
    assert len(deck)==len(by_word)==120
    return deck

def plural(word):
    if word in IRREGULAR_PLURAL: return IRREGULAR_PLURAL[word]
    head=word.split()[-1]
    plural_head=head[:-1]+'ies' if head.endswith('y') and head[-2] not in 'aeiou' else head+'es' if head.endswith(('s','x','z','ch','sh')) or head in {'potato','tomato'} else head+'s'
    return ' '.join(word.split()[:-1]+[plural_head])

def update_table(path,rows):
    words={row[0] for row in rows}
    prior=[line for line in path.read_text(encoding='utf-8').splitlines() if line.split('\t')[0] not in words]
    path.write_text('\n'.join(prior+['\t'.join(row) for row in rows])+'\n',encoding='utf-8')

if __name__ == '__main__':
    data=build()
    for path in [ROOT/'decks'/DECK]: write(path,data)
    update_table(ROOT/'tools/verb-forms.tsv',lines(VERBS))
    noun_rows=[]
    for w in data:
        if not any(s['pos']=='noun' for s in [w]+w.get('senses',[])): continue
        base=w['word']
        status='mass' if base in MASS else 'lexical_plural' if base in LEXICAL_PLURAL else 'invariant' if base=='fish' else 'countable'
        noun_rows.append([base,status,str(len(base.split())-1),plural(base) if status=='countable' else base if status=='invariant' else ''])
    update_table(ROOT/'tools/noun-forms.tsv',noun_rows)
    pairs=[dict(word=w['word'],sourceGroup='basic-120',**{k:s[k] for k in ('pos','meaningVi','example','exampleVi')}) for w in data for s in [w]+w.get('senses',[])]
    write(ROOT/'tools/curated-basic-120-examples.json',pairs)
    curated=['curated-sense-examples.json','curated-awl-examples.json','curated-b2-examples.json',
        'curated-core-examples.json','curated-b2-daily-work-examples.json','curated-daily-work-498-examples.json',
        'curated-professional-examples.json','curated-reviewed-examples.json','curated-basic-20-examples.json',
        'curated-basic-120-examples.json','curated-everyday-500-examples.json','curated-prepositions-examples.json']
    write(ROOT/'learning/sense-examples.json',sum((json.loads((ROOT/'tools'/name).read_text(encoding='utf-8')) for name in curated),[]))
    for path in [ROOT/'catalog.json']:
        catalog=json.loads(path.read_text(encoding='utf-8'))
        catalog['files']=[f for f in catalog['files'] if f['url']!='decks/'+DECK]
        catalog['files'].insert(2,dict(title='Thông dụng · 120 từ bổ sung',count=120,url='decks/'+DECK,
            description='120 từ/cụm mới trong 6 nhóm: động từ, đồ dùng, thực phẩm, quần áo, cơ thể và đi lại. IPA, ví dụ Anh–Việt, dạng chia và đồng nghĩa phù hợp; có sẵn offline trên Windows/Android.'))
        write(path,catalog)
    forms=runpy.run_path(str(ROOT/'tools/build-word-forms.py'))
    payload=forms['build_payload']()
    forms['write'](forms['PAYLOAD'],payload)
    for path in ['learning/word-forms.json']: forms['write'](ROOT/path,payload)
    forms['apply_to_decks'](payload)
    print(f'PASS: built 120 roots, {len(pairs)} bilingual contexts and reviewed noun/verb forms.')
