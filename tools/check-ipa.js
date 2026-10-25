#!/usr/bin/env node
/**
 * Soát IPA trong seed_words.json.
 *
 * Chạy:  node tools/check-ipa.js [thư-mục-chứa-en_UK.txt]
 *
 * Từ điển tham chiếu lấy từ https://github.com/open-dict-data/ipa-dict
 * (tải data/en_UK.txt và data/en_US.txt về cùng một thư mục rồi trỏ tham số vào đó).
 * Không có từ điển thì script vẫn chạy phần kiểm tự thân.
 *
 * LƯU Ý VỀ PHƯƠNG PHÁP: ipa-dict sinh bằng eSpeak-NG, dùng quy ước khác kiểu từ điển
 * Cambridge mà bộ seed đang theo (ɹ thay r, ɐ thay ə, không dấu ngắt âm tiết, và hay
 * chọn nhầm từ loại với các cặp đồng tự như combine/refuse/moderate). Vì vậy nó KHÔNG
 * phải chân lý — script chỉ chuẩn hoá cả hai về cùng bộ xương âm vị rồi **xếp hạng chỗ
 * đáng ngờ để người soi tay**, chứ không tự sửa.
 */
const fs = require('fs');
const path = require('path');

const SEED = path.join(__dirname, '..', 'seed_words.json');

// Tham số: [thư-mục-từ-điển] [--file <đường-dẫn>]
// --file để soát các bộ từ rời (decks/ielts-*.json) chứ không chỉ bộ seed kèm app.
const args = process.argv.slice(2);
const fileFlag = args.indexOf('--file');
const target = fileFlag >= 0 ? args[fileFlag + 1] : SEED;
const dictDir = args.filter((a, i) => a !== '--file' && i !== fileFlag + 1)[0];

console.log('soát file:', path.relative(path.join(__dirname, '..'), target));
const words = JSON.parse(fs.readFileSync(target, 'utf8'));

// ---------- kiểm tự thân, không cần từ điển ----------

const VOWELS = 'iɪeɛæaɑɒɔoʊuʌəɜɐ';
const badFormat = [];
const dupes = [];
const seen = new Map();

for (const w of words) {
  if (!/^\/.+\/$/.test(w.ipa || '')) badFormat.push(`${w.word}: ${w.ipa}`);
  if (seen.has(w.ipa)) dupes.push(`${w.word} dùng chung IPA với ${seen.get(w.ipa)}: ${w.ipa}`);
  else seen.set(w.ipa, w.word);
}

/**
 * Đếm âm tiết bằng **ranh giới**: mỗi dấu chấm và mỗi dấu trọng âm không đứng đầu đều mở
 * một âm tiết mới. Cách này đúng tuyệt đối với quy ước của bộ seed, và quan trọng hơn là
 * nó xử lý được /ˈbaɪ.əs/ — nguyên âm đôi đi liền nguyên âm khác, thứ mà phép đếm cụm
 * nguyên âm luôn đếm nhầm thành một.
 */
function syllablesByBoundary(ipa) {
  const body = (ipa || '').replace(/[\/]/g, '');
  const dots = (body.match(/\./g) || []).length;
  // Dấu trọng âm ở ngay đầu chuỗi không mở thêm âm tiết nào.
  const marks = (body.slice(1).match(/[ˈˌ]/g) || []).length;
  // Cụm nhiều chữ: khoảng trắng giữa các chữ cũng là ranh giới âm tiết. Thiếu dòng này thì
  // mọi mục dạng cụm (`evidence-based`, `peer review`) đều bị báo nhầm là thiếu dấu ngắt.
  const spaces = (body.match(/ (?![ˈˌ])/g) || []).length;
  return dots + marks + spaces + 1;
}

/**
 * Đếm bằng cụm nguyên âm liền nhau, giữ lại làm phép đối chiếu.
 *
 * LƯU Ý: bản trước khởi tạo `prev = ''`, mà `'abc'.includes('')` trong JS trả về **true**,
 * nên nguyên âm đầu tiên không bao giờ được đếm. Hậu quả là 110/1002 mục lọt khỏi phép
 * kiểm trọng âm mà không ai biết — mọi từ mở đầu bằng nguyên âm và chỉ có hai âm tiết.
 * Phải là `prev = null`.
 */
function syllablesByVowel(ipa) {
  const body = (ipa || '').replace(/[\/ˈˌ.]/g, '');
  let syl = 0, prev = null;
  for (const c of body) {
    if (VOWELS.includes(c) && !(prev !== null && VOWELS.includes(prev))) syl++;
    prev = c;
  }
  return syl;
}

const noStress = [];
const extraStress = [];
const dotSuspect = [];
for (const w of words) {
  if (w.word.includes(' ')) continue;
  const byBoundary = syllablesByBoundary(w.ipa);
  const byVowel = syllablesByVowel(w.ipa);
  if (byBoundary > 1 && !(w.ipa || '').includes('ˈ')) noStress.push(`${w.word}: ${w.ipa}`);
  // Từ đơn âm tiết không mang dấu trọng âm: /bætʃ/, không phải /ˈbætʃ/.
  if (byBoundary === 1 && (w.ipa || '').includes('ˈ')) extraStress.push(`${w.word}: ${w.ipa}`);
  // Hai cách đếm lệch nhau thì gần như chắc chắn là thiếu một dấu ngắt âm tiết.
  if (byVowel > byBoundary) {
    dotSuspect.push(`${w.word}: ${w.ipa} (${byBoundary} dấu ngắt / ${byVowel} nguyên âm)`);
  }
}

console.log('tổng từ               :', words.length);
console.log('sai định dạng /.../   :', badFormat.length);
console.log('trùng IPA giữa các từ :', dupes.length);
console.log('thiếu dấu trọng âm    :', noStress.length);
console.log('thừa trọng âm (1 âm tiết):', extraStress.length);
console.log('nghi thiếu dấu ngắt   :', dotSuspect.length);
[...badFormat, ...dupes, ...noStress, ...extraStress, ...dotSuspect]
  .slice(0, 25).forEach(s => console.log('   - ' + s));

if (!dictDir) {
  console.log('\n(không truyền thư mục từ điển nên bỏ qua phần đối chiếu)');
  process.exit(
    badFormat.length || dupes.length || noStress.length || extraStress.length ? 1 : 0
  );
}

// ---------- đối chiếu từ điển ----------

function loadDict(file) {
  const map = new Map();
  const full = path.join(dictDir, file);
  if (!fs.existsSync(full)) return map;
  for (const line of fs.readFileSync(full, 'utf8').split('\n')) {
    const [w, ipas] = line.split('\t');
    if (w && ipas) map.set(w.trim().toLowerCase(), ipas.split(',')[0].trim());
  }
  return map;
}
const uk = loadDict('en_UK.txt');
const us = loadDict('en_US.txt');
if (!uk.size && !us.size) {
  console.log('\nKhông đọc được en_UK.txt / en_US.txt trong', dictDir);
  process.exit(1);
}

const FOLD = [
  [/[\/\[\]]/g, ''], [/[ˈˌ]/g, ''], [/\./g, ''], [/\s+/g, ''], [/ː/g, ''],
  [/ɹ/g, 'r'], [/ɐ/g, 'ə'], [/ᵻ/g, 'ɪ'], [/ɚ/g, 'ər'], [/ɝ/g, 'ɜr'], [/ɫ/g, 'l'],
  [/ɡ/g, 'g'], [/oʊ/g, 'əʊ'], [/ɑ/g, 'ɒ'], [/æ/g, 'a'], [/ʌ/g, 'a'],
  [/ə/g, 'a'], [/ɛ/g, 'e'], [/ɔ/g, 'o'], [/ʊ/g, 'u'], [/ɪ/g, 'i'],
];
const skeleton = s => FOLD.reduce((acc, [re, to]) => acc.replace(re, to), s || '');

function lev(a, b) {
  const m = Array.from({ length: a.length + 1 }, (_, i) => [i, ...Array(b.length).fill(0)]);
  for (let j = 0; j <= b.length; j++) m[0][j] = j;
  for (let i = 1; i <= a.length; i++)
    for (let j = 1; j <= b.length; j++)
      m[i][j] = Math.min(m[i-1][j]+1, m[i][j-1]+1, m[i-1][j-1] + (a[i-1] === b[j-1] ? 0 : 1));
  return m[a.length][b.length];
}

/** Âm tiết thứ mấy mang trọng âm chính. Đây là phép so đáng tin nhất giữa hai quy ước. */
function stressIndex(ipa) {
  const s = (ipa || '').replace(/[\/.]/g, '').replace(/ˌ/g, '');
  const at = s.indexOf('ˈ');
  if (at < 0) return 0;
  let n = 0, prev = null;
  for (let k = 0; k < at; k++) {
    if (VOWELS.includes(s[k]) && !(prev !== null && VOWELS.includes(prev))) n++;
    prev = s[k];
  }
  return n;
}

const diverged = [], stressDiff = [];
let compared = 0, notFound = 0;

for (const w of words) {
  if (w.word.includes(' ') || w.word.includes('-')) continue;
  const key = w.word.toLowerCase();
  const ref = uk.get(key) || us.get(key);
  if (!ref) { notFound++; continue; }
  compared++;
  const a = skeleton(w.ipa), b = skeleton(ref);
  const ratio = lev(a, b) / Math.max(a.length, b.length, 1);
  if (ratio > 0.18) diverged.push({ w: w.word, mine: w.ipa, ref, ratio });
  if (stressIndex(w.ipa) !== stressIndex(ref)) stressDiff.push({ w: w.word, mine: w.ipa, ref });
}

diverged.sort((x, y) => y.ratio - x.ratio);

console.log('\nđối chiếu được        :', compared, '(không tra được:', notFound + ')');
console.log('lệch âm vị >18%       :', diverged.length);
diverged.forEach(d => console.log(`   - ${d.w}: ${d.mine}  vs  ${d.ref}  (${(d.ratio * 100).toFixed(0)}%)`));
console.log('lệch vị trí trọng âm  :', stressDiff.length);
stressDiff.forEach(d => console.log(`   - ${d.w}: ${d.mine}  vs  ${d.ref}`));

console.log(
  '\nMọi mục trên đây chỉ là NGHI VẤN, phải soi tay. Phần lớn hoá ra là khác biệt Anh-Mỹ,\n' +
  'cặp đồng tự khác âm theo từ loại, hoặc chính eSpeak sai.'
);
