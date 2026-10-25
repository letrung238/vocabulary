#!/usr/bin/env node
/**
 * Tách trường `topic` ra khỏi `tags` trong các bộ từ.
 *
 *   node tools/split-topic.js [--write]
 *
 * VÌ SAO. Lúc đầu mọi thứ nhét chung vào `tags`, và nó trộn ba loại khác hẳn nhau:
 * chủ đề nội dung (environment), tên bộ (awl, task1), và nhãn kỹ thuật của riêng bộ Task 1
 * (trend-up, hedge). Hậu quả là hàng chip lọc trong app hiện 20 lựa chọn lẫn lộn, người dùng
 * thấy "hedge" nằm cạnh "Môi trường" mà không hiểu đó là gì.
 *
 * Sau khi tách:
 *   topic  một giá trị, lấy từ danh sách đóng — thứ dùng để "học theo chủ đề"
 *   tags   phần còn lại: tên bộ và nhãn kỹ thuật, vẫn giữ vì chúng có thông tin
 *
 * `noun` bị bỏ hẳn: nó trùng nghĩa với trường `pos` vốn đã có.
 */
const fs = require('fs');
const path = require('path');

const TOPICS = new Set([
  'environment', 'education', 'technology', 'health', 'society', 'work',
  'economy', 'media', 'law',
]);
const DROP = new Set(['noun']);

const write = process.argv.includes('--write');
const dir = path.join(__dirname, '..', 'decks');
let changed = 0, multi = 0, stats = {};

for (const file of fs.readdirSync(dir).filter(f => f.endsWith('.json')).sort()) {
  const p = path.join(dir, file);
  const words = JSON.parse(fs.readFileSync(p, 'utf8'));
  let n = 0;
  for (const w of words) {
    const tags = (w.tags || []).filter(t => !DROP.has(t));
    const topics = tags.filter(t => TOPICS.has(t));
    const rest = tags.filter(t => !TOPICS.has(t));

    // Từ thuộc nhiều chủ đề là chuyện thật: `stigma` vừa sức khoẻ vừa xã hội. Chủ đề đầu
    // vào `topic`, các chủ đề còn lại **giữ trong `tags`** — bộ lọc trong app so cả hai
    // trường, nên lọc theo "society" vẫn ra `stigma`. Vứt chúng đi là mất thông tin thật.
    const topic = topics[0] || '';
    const extraTopics = topics.slice(1);

    if (topic) { w.topic = topic; stats[topic] = (stats[topic] || 0) + 1; }
    else delete w.topic;
    const keep = [...rest, ...extraTopics];
    if (keep.length) w.tags = keep; else delete w.tags;
    if (extraTopics.length) multi++;
    n++;
  }
  if (write) fs.writeFileSync(p, JSON.stringify(words, null, 2) + '\n');
  console.log(`  ${file.padEnd(28)} ${n} từ`);
  changed += n;
}

console.log('\nchủ đề sau khi tách:');
for (const [t, n] of Object.entries(stats).sort((a, b) => b[1] - a[1])) {
  console.log(`  ${t.padEnd(14)} ${n}`);
}
const noTopic = changed - Object.values(stats).reduce((a, b) => a + b, 0);
console.log(`  ${'(không có)'.padEnd(14)} ${noTopic}   ← bộ Task 1 và AWL thuần kỹ năng`);
console.log(`\n${multi} từ thuộc nhiều chủ đề — chủ đề phụ giữ trong tags`);
console.log(write ? 'Đã ghi.' : '(xem trước — thêm --write để ghi)');
