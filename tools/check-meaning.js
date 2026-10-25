#!/usr/bin/env node
/**
 * Soát nghĩa tiếng Việt và câu ví dụ. Chạy: node tools/check-meaning.js
 *
 * Không có từ điển nào diff được ngữ nghĩa, nên script chỉ kiểm các bất biến cấu trúc.
 * Phép mạnh nhất là "câu ví dụ phải chứa chính từ đó" — nó bắt được lỗi copy nhầm câu.
 * Lưu ý: bộ sinh dạng biến thể không biết động từ bất quy tắc (overcome -> overcame) và
 * từ có gạch nối, nên các mục đó sẽ bị báo nhầm. Soi tay trước khi sửa.
 *
 * Nghĩa có ĐÚNG hay không thì script không biết — phần đó vẫn phải đọc.
 */
// Soát nghĩa tiếng Việt và câu ví dụ trong seed_words.json.
// Không có từ điển để diff, nên dựa vào các bất biến cấu trúc.
const fs = require('fs');
const path = require('path');

/**
 * Mặc định soát bộ seed kèm app. Truyền đường dẫn thì soát các file đó thay vào.
 *
 * Truyền **nhiều file** thì mọi phép kiểm trùng lặp (câu ví dụ, nghĩa tiếng Việt) chạy trên
 * hợp của tất cả — đây mới là điều cần biết khi thêm một bộ từ mới: người dùng sẽ gộp nó
 * vào cùng deck với bộ cũ, nên hai bộ trùng nghĩa nhau cũng tai hại y như trùng trong một bộ.
 */
const argFiles = process.argv.slice(2).filter(a => !a.startsWith('--'));
const files = argFiles.length
  ? argFiles
  : [path.join(__dirname, '..', 'seed_words.json')];

const words = [];
for (const f of files) {
  const part = JSON.parse(fs.readFileSync(f, 'utf8'));
  console.log('nạp', path.relative(path.join(__dirname, '..'), f), ':', part.length, 'từ');
  for (const w of part) words.push({ ...w, __src: path.basename(f) });
}

const VI_CHARS = /[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]/i;

// Sinh các dạng biến thể có thể có của một từ, để tìm trong câu ví dụ.
function forms(w) {
  const b = w.toLowerCase();
  const out = new Set([b]);
  const add = s => out.add(s);
  add(b + 's'); add(b + 'es'); add(b + 'ed'); add(b + 'd'); add(b + 'ing');
  add(b + 'ly'); add(b + 'r'); add(b + 'st');
  if (b.endsWith('e')) { const s = b.slice(0, -1); add(s + 'ing'); add(s + 'ed'); add(s + 'es'); }
  if (b.endsWith('y')) { const s = b.slice(0, -1); add(s + 'ies'); add(s + 'ied'); add(s + 'ier'); add(s + 'iest'); }
  if (/[^aeiou][aeiou][^aeiouwxy]$/.test(b)) { const c = b + b.slice(-1); add(c + 'ing'); add(c + 'ed'); }
  if (b.endsWith('ise') || b.endsWith('ize')) { const s = b.slice(0, -1); add(s + 'ing'); add(s + 'd'); add(s + 's'); }
  if (b.endsWith('ify')) { const s = b.slice(0, -1); add(s + 'ies'); add(s + 'ied'); }
  // 'qu' đứng như một phụ âm: equip -> equipped. Luật nhân đôi phụ âm ở trên không bắt
  // được vì nó thấy 'u' là nguyên âm.
  if (/qu[aeiou][^aeiouwxy]$/.test(b)) { const c = b + b.slice(-1); add(c + 'ing'); add(c + 'ed'); }
  // Động từ bất quy tắc, khớp theo ĐUÔI chứ không theo cả từ — nhờ vậy một dòng lo được
  // cả take/undertake/overtake, come/overcome/become, draw/withdraw.
  for (const [suffix, forms] of IRREGULAR) {
    if (b.endsWith(suffix) && b.length >= suffix.length) {
      const stem = b.slice(0, b.length - suffix.length);
      for (const f of forms) add(stem + f);
    }
  }
  return out;
}

/** đuôi nguyên thể -> các dạng quá khứ / phân từ. Đủ dùng cho từ vựng học thuật. */
const IRREGULAR = [
  ['take', ['took', 'taken']], ['come', ['came']], ['give', ['gave', 'given']],
  ['draw', ['drew', 'drawn']], ['hold', ['held']], ['stand', ['stood']],
  ['seek', ['sought']], ['think', ['thought']], ['bring', ['brought']],
  ['lead', ['led']], ['mean', ['meant']], ['write', ['wrote', 'written']],
  ['rise', ['rose', 'risen']], ['fall', ['fell', 'fallen']], ['grow', ['grew', 'grown']],
  ['speak', ['spoke', 'spoken']], ['break', ['broke', 'broken']],
  ['choose', ['chose', 'chosen']], ['find', ['found']], ['make', ['made']],
  ['pay', ['paid']], ['say', ['said']], ['see', ['saw', 'seen']],
  ['show', ['showed', 'shown']], ['run', ['ran']], ['win', ['won']],
  ['lose', ['lost']], ['keep', ['kept']], ['leave', ['left']], ['feel', ['felt']],
  ['build', ['built']], ['send', ['sent']], ['spend', ['spent']],
  ['bear', ['bore', 'borne']], ['arise', ['arose', 'arisen']], ['prove', ['proved', 'proven']],
];

function tokens(sentence) {
  return (sentence || '').toLowerCase().split(/[^a-z]+/).filter(Boolean);
}

const missingInExample = [], dupExample = [], dupExampleVi = [], sameAsMeaning = [];
const badPunct = [], viInEnglish = [], englishInVi = [], lengthOdd = [], emptyish = [];
const seenEx = new Map(), seenExVi = new Map(), meaningCount = new Map();

for (const w of words) {
  const { word, meaningVi, example, exampleVi } = w;

  if (!meaningVi?.trim() || !example?.trim() || !exampleVi?.trim()) {
    emptyish.push(word); continue;
  }

  // 1. câu ví dụ phải chứa từ đó (hoặc một dạng biến thể)
  const f = forms(word.replace(/[^a-zA-Z ]/g, ''));
  const t = tokens(example);
  // Cụm từ: động từ đứng đầu vẫn chia bình thường, nên "queue up" phải khớp "queued up".
  // So từng mảnh thay vì so nguyên chuỗi.
  let phraseHit = false;
  if (word.includes(' ')) {
    const parts = word.toLowerCase().split(/\s+/);
    const tks = tokens(example);
    // Mọi chữ trong cụm đều chia dạng được: động từ cụm chia ở chữ đầu (`queued up`),
    // còn cụm danh từ số nhiều lại chia ở chữ cuối (`household chores`).
    const allOk = parts.every(p => [...forms(p)].some(x => tks.includes(x)));
    phraseHit = allOk || example.toLowerCase().includes(word.toLowerCase());
  }
  // Từ có gạch nối: so khớp sau khi bỏ hết ký tự không phải chữ cái ở cả hai phía.
  // `forms()` sinh biến thể từ "onpremise" nên không bao giờ khớp "on-premise" trong câu,
  // và đó là lý do 7 mục hợp lệ của bộ seed bị báo nhầm suốt từ đầu.
  const stripped = x => x.toLowerCase().replace(/[^a-z]/g, '');
  const hyphenHit = /-/.test(word) && stripped(example).includes(stripped(word));
  if (!phraseHit && !hyphenHit && ![...f].some(x => t.includes(x))) {
    missingInExample.push(`${word}  ->  ${example}`);
  }

  // 2. trùng câu giữa các từ
  if (seenEx.has(example)) dupExample.push(`${word} [${w.__src}] == ${seenEx.get(example)}: ${example}`);
  else seenEx.set(example, word);
  if (seenExVi.has(exampleVi)) dupExampleVi.push(`${word} [${w.__src}] == ${seenExVi.get(exampleVi)}: ${exampleVi}`);
  else seenExVi.set(exampleVi, word);

  // 3. bản dịch không được trùng y nguyên phần nghĩa
  if (exampleVi.trim().toLowerCase() === meaningVi.trim().toLowerCase()) sameAsMeaning.push(word);

  // 4. dấu câu
  if (!/^[A-Z"']/.test(example) || !/[.!?]$/.test(example)) badPunct.push(`EN ${word}: ${example}`);
  if (!/[.!?]$/.test(exampleVi)) badPunct.push(`VI ${word}: ${exampleVi}`);

  // 5. lẫn ngôn ngữ
  if (VI_CHARS.test(example)) viInEnglish.push(`${word}: ${example}`);
  if (!VI_CHARS.test(exampleVi) && exampleVi.split(/\s+/).length > 3) englishInVi.push(`${word}: ${exampleVi}`);

  // 6. độ dài lệch bất thường giữa hai câu
  const r = exampleVi.length / example.length;
  if (r < 0.5 || r > 2.0) lengthOdd.push(`${word}  (${r.toFixed(2)})  EN: ${example}  |  VI: ${exampleVi}`);

  meaningCount.set(meaningVi, (meaningCount.get(meaningVi) || 0) + 1);
}

// Chỉ báo khi hai từ **khác nhau** chung một nghĩa. Cùng một từ xuất hiện ở hai file là
// chuyện bình thường và có chủ đích: bộ theo chủ đề khai lại từ đã có trong bộ chính chỉ
// để gắn thêm `topic` cho nó, và lúc import gộp thì hai bản nhập làm một.
const dupMeaning = [...meaningCount.entries()].filter(([, n]) => n > 1)
  .map(m => m[0])
  .filter(m => new Set(words.filter(w => w.meaningVi === m).map(w => w.word.toLowerCase())).size > 1)
  .map(m => `"${m}" dùng cho ${new Set(words.filter(w => w.meaningVi === m).map(w => w.word)).size} từ: `
    + words.filter(w => w.meaningVi === m).map(w => `${w.word} [${w.__src}]`).join(', '));

const show = (title, arr, limit = 25) => {
  console.log(`\n=== ${title}: ${arr.length} ===`);
  arr.slice(0, limit).forEach(s => console.log('  ' + s));
  if (arr.length > limit) console.log(`  ... còn ${arr.length - limit} mục`);
};

console.log('tổng từ:', words.length);
show('THIẾU TRƯỜNG', emptyish);
show('CÂU VÍ DỤ KHÔNG CHỨA TỪ', missingInExample, 40);
show('TRÙNG CÂU VÍ DỤ (EN)', dupExample);
show('TRÙNG CÂU DỊCH (VI)', dupExampleVi);
show('CÂU DỊCH TRÙNG PHẦN NGHĨA', sameAsMeaning);
show('SAI DẤU CÂU / VIẾT HOA', badPunct, 15);
show('LẪN TIẾNG VIỆT TRONG CÂU EN', viInEnglish);
show('CÂU VI KHÔNG CÓ DẤU TIẾNG VIỆT', englishInVi);
show('ĐỘ DÀI LỆCH BẤT THƯỜNG', lengthOdd, 15);
show('NGHĨA VIỆT TRÙNG NHAU', dupMeaning, 20);
