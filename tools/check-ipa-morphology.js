#!/usr/bin/env node
/**
 * Soát IPA của những từ KHÔNG có trong từ điển tham chiếu — chủ yếu là thuật ngữ IT mới
 * (webhook, idempotent, observability...). Từ điển không có chúng, nhưng hình thái của
 * chúng thì kiểm được:
 *
 *   compound  ghép IPA của các thành phần   (uptime = up + time)
 *   derive    suy từ gốc rồi thay/thêm phụ tố (concurrency <- concurrent)
 *   rhyme     đối chiếu đuôi với lớp từ cùng vần CÓ trong từ điển (minify ~ nullify)
 *
 * Chạy:  node tools/check-ipa-morphology.js <thư-mục-chứa-en_UK.txt>
 * Từ điển: https://github.com/open-dict-data/ipa-dict (data/en_UK.txt, data/en_US.txt)
 *
 * Thêm thuật ngữ mới vào seed thì thêm một dòng vào COMPOUND / DERIVE / RHYME bên dưới.
 *
 * Cẩn thận khi chọn từ neo cho `rhyme`: neo phải cùng cấu trúc âm, đừng chỉ cùng chữ cái.
 * Ví dụ minify KHÔNG neo được vào magnify/signify vì chúng có "g" mà minify không có.
 */
const fs = require('fs');
const path = require('path');

const dictDir = process.argv[2];
if (!dictDir) {
  console.error('Cần đường dẫn tới thư mục chứa en_UK.txt và en_US.txt');
  process.exit(2);
}

const SEED = path.join(__dirname, '..', 'seed_words.json');
const mine = new Map(JSON.parse(fs.readFileSync(SEED, 'utf8')).map(w => [w.word, w.ipa]));

function loadDict(file) {
  const m = new Map();
  const full = path.join(dictDir, file);
  if (!fs.existsSync(full)) return m;
  for (const line of fs.readFileSync(full, 'utf8').split('\n')) {
    const [w, i] = line.split('\t');
    if (w && i) m.set(w.trim().toLowerCase(), i.split(',')[0].trim());
  }
  return m;
}
const uk = loadDict('en_UK.txt'), us = loadDict('en_US.txt');
const ref = w => uk.get(w) || us.get(w);

const FOLD = [
  [/[\/\[\]]/g, ''], [/[ˈˌ]/g, ''], [/\./g, ''], [/\s+/g, ''], [/ː/g, ''],
  [/ɹ/g, 'r'], [/ɐ/g, 'ə'], [/ᵻ/g, 'ɪ'], [/ɚ/g, 'ər'], [/ɝ/g, 'ɜr'], [/ɫ/g, 'l'],
  [/ɡ/g, 'g'], [/oʊ/g, 'əʊ'], [/ɑ/g, 'ɒ'], [/æ/g, 'a'], [/ʌ/g, 'a'],
  [/ə/g, 'a'], [/ɛ/g, 'e'], [/ɔ/g, 'o'], [/ʊ/g, 'u'], [/ɪ/g, 'i'], [/r$/g, ''],
];
const sk = s => FOLD.reduce((a, [r, t]) => a.replace(r, t), s || '');

const COMPOUND = {
  breakpoint: ['break', 'point'], changelog: ['change', 'log'], cutover: ['cut', 'over'],
  failover: ['fail', 'over'], frontend: ['front', 'end'], fullstack: ['full', 'stack'],
  hotfix: ['hot', 'fix'], middleware: ['middle', 'ware'], onboarding: ['on', 'boarding'],
  runbook: ['run', 'book'], runtime: ['run', 'time'], stacktrace: ['stack', 'trace'],
  uptime: ['up', 'time'], viewport: ['view', 'port'], webhook: ['web', 'hook'],
  wireframe: ['wire', 'frame'],
};

// [từ, gốc, đuôi-gốc-bỏ-đi (null = thêm tiền tố), đuôi/tiền-tố mới]
const DERIVE = [
  ['concurrency', 'concurrent', 'ənt', 'ənsi'],
  ['observability', 'observable', 'əbəl', 'əbiliti'],
  ['recursion', 'recur', '', 'ʃən'],
  ['versioning', 'version', '', 'ɪŋ'],
  ['refactor', 'factor', null, 'riː'],
  ['deprioritize', 'prioritize', null, 'diː'],
];

// [từ, mô tả lớp vần, các từ neo có trong từ điển]
const RHYME = [
  ['minify', '-ify không có g', ['nullify', 'clarify', 'verify']],
  ['idempotent', '-potent', ['potent', 'impotent', 'omnipotent']],
  ['nullable', '-able', ['capable', 'reliable', 'suitable']],
];

const rows = [];
const add = (w, how, expect, ok) => rows.push([w, how, mine.get(w) || '(không có trong seed)', expect, ok]);

for (const [w, parts] of Object.entries(COMPOUND)) {
  if (!mine.has(w)) continue;
  const refs = parts.map(ref);
  if (refs.some(r => !r)) { add(w, 'compound', 'thiếu thành phần', null); continue; }
  add(w, 'compound', refs.join(' + '), sk(mine.get(w)) === sk(refs.join('')));
}

for (const [w, base, drop, extra] of DERIVE) {
  if (!mine.has(w)) continue;
  const b = ref(base);
  if (!b) { add(w, 'derive', 'gốc "' + base + '" không có trong từ điển', null); continue; }
  const want = drop === null
    ? sk(extra) + sk(b)
    : sk(b).replace(new RegExp(sk(drop) + '$'), '') + sk(extra);
  add(w, 'derive', base + ' ' + b + ' => ' + want, sk(mine.get(w)) === want);
}

for (const [w, label, anchors] of RHYME) {
  if (!mine.has(w)) continue;
  const tails = anchors.map(a => ref(a)).filter(Boolean).map(sk);
  if (!tails.length) { add(w, 'rhyme', 'không có từ neo', null); continue; }
  let common = tails[0];
  for (const t of tails.slice(1)) {
    let k = 0;
    while (k < common.length && k < t.length && common.at(-1 - k) === t.at(-1 - k)) k++;
    common = common.slice(common.length - k);
  }
  add(w, 'rhyme', label + ' (' + anchors.join(', ') + ') => đuôi "' + common + '"',
    sk(mine.get(w)).endsWith(common));
}

rows.sort((a, b) => a[0].localeCompare(b[0]));
const pad = (s, n) => (String(s) + ' '.repeat(n)).slice(0, n);
console.log(pad('TỪ', 16) + pad('CÁCH', 10) + pad('IPA CỦA TÔI', 24) + pad('ĐỐI CHIẾU', 46) + 'KẾT QUẢ');
console.log('-'.repeat(106));
for (const [w, how, ipa, expect, ok] of rows) {
  console.log(pad(w, 16) + pad(how, 10) + pad(ipa, 24) + pad(expect, 46) +
    (ok === null ? 'không kiểm được' : ok ? 'khớp' : 'LỆCH - soi tay'));
}
const bad = rows.filter(r => r[4] === false);
console.log('\nkhớp:', rows.filter(r => r[4] === true).length + '/' + rows.length);
if (bad.length) {
  console.log(
    'Mục LỆCH chỉ là nghi vấn. Nguyên nhân thường gặp: khác biệt Anh-Mỹ trong từ điển\n' +
    'tham chiếu, hoặc từ neo chọn sai lớp vần. Soi tay trước khi sửa.'
  );
}
