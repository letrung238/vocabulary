#!/usr/bin/env node
/**
 * Điền IPA vào một file bộ từ còn để trống trường `ipa`, lấy gợi ý từ ipa-suggest.js.
 *
 * Chạy:  node tools/ipa-fill.js <thư-mục-ipa-dict> <file.json> [--write]
 *
 * Không có --write thì chỉ in ra xem trước, không đụng file.
 *
 * VÌ SAO TÁCH KHỎI VIỆC VIẾT NGHĨA. Hai việc có tính chất khác hẳn nhau: nghĩa tiếng Việt
 * và câu ví dụ cần người quyết, còn IPA cần **nhất quán** — cùng một quy ước cho cả nghìn
 * mục. Máy làm phần nhất quán tốt hơn người, người làm phần phán đoán tốt hơn máy.
 *
 * Mục nào tra không ra, hoặc nghi ngờ (chỉ có trong từ điển Anh-Mỹ), đều được liệt kê
 * riêng ở cuối để soi tay. Từ có dấu cách hoặc gạch nối thì bỏ qua — cụm từ phải tự viết.
 */
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const dictDir = process.argv[2];
const file = process.argv[3];
const write = process.argv.includes('--write');

if (!dictDir || !file) {
  console.error('Dùng: node tools/ipa-fill.js <thư-mục-ipa-dict> <file.json> [--write]');
  process.exit(2);
}

const words = JSON.parse(fs.readFileSync(file, 'utf8'));
const need = words.filter(w => !w.ipa || !w.ipa.trim());
const single = need.filter(w => !/[\s-]/.test(w.word));

if (!single.length) {
  console.log('Không có mục nào cần điền.');
  process.exit(0);
}

const out = execFileSync(
  'node',
  [path.join(__dirname, 'ipa-suggest.js'), dictDir, '-'],
  { input: single.map(w => w.word).join('\n'), encoding: 'utf8' }
);

const suggestion = new Map();
const flagged = [];
const notFound = [];
for (const line of out.split('\n')) {
  if (!line.trim()) continue;
  const [word, ipa, flags] = line.split('\t');
  if (!ipa || ipa === '' || flags === 'KHÔNG-TRA-ĐƯỢC') { notFound.push(word); continue; }
  suggestion.set(word, ipa);
  if (flags && flags.trim()) flagged.push(`${word}\t${ipa}\t${flags}`);
}

let filled = 0;
for (const w of words) {
  if (w.ipa && w.ipa.trim()) continue;
  const s = suggestion.get(w.word);
  if (s) { w.ipa = s; filled++; }
}

console.log('cần điền        :', need.length);
console.log('điền được       :', filled);
console.log('tra không ra    :', notFound.length, notFound.length ? '→ ' + notFound.join(', ') : '');
console.log('cụm từ, tự viết :', need.length - single.length);

if (flagged.length) {
  console.log('\nCẦN SOI TAY (' + flagged.length + '):');
  flagged.forEach(f => console.log('  ' + f));
}

if (write) {
  fs.writeFileSync(file, JSON.stringify(words, null, 2) + '\n', 'utf8');
  console.log('\nĐã ghi vào', file);
} else {
  console.log('\n(xem trước — thêm --write để ghi)');
}
