#!/usr/bin/env node
/** Review aid only: no dictionary candidates are published to a deck automatically. */
const fs = require('node:fs');
const path = require('node:path');
const sourceDir = process.argv[2];
if (!sourceDir || !fs.existsSync(sourceDir)) {
  console.error('Usage: node tools/prepare-sense-candidates.js <dictionary-jsonl-directory>');
  process.exit(2);
}
const root = path.resolve(__dirname, '..');
const files = ['seed_words.json', ...fs.readdirSync(path.join(root, 'decks'))
  .filter(name => name.endsWith('.json')).sort().map(name => `decks/${name}`)];
const needed = new Set(files.flatMap(file => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8')))
  .filter(word => !word.senses?.length).map(word => word.word.toLowerCase()));
const index = new Map();
for (const file of fs.readdirSync(sourceDir).filter(name => name.endsWith('.jsonl'))) {
  for (const line of fs.readFileSync(path.join(sourceDir, file), 'utf8').split(/\r?\n/)) {
    if (!line) continue;
    const entry = JSON.parse(line);
    const key = entry.headword?.toLowerCase();
    if (!needed.has(key)) continue;
    if (!index.has(key)) index.set(key, []);
    index.get(key).push({ pos: entry.pos, vi: entry.senses_vi, en: entry.senses_en,
      gloss: entry.gloss_en, confidence: entry.extra?.llm_confidence });
  }
}
const output = path.join(root, 'build/sense-candidates.json');
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, JSON.stringify(Object.fromEntries([...index].sort()), null, 2));
const multiple = [...index].filter(([, entries]) => entries.reduce((n, e) => n + e.vi.length, 0) > 1);
console.log(`Words missing a secondary sense: ${needed.size}`);
console.log(`Dictionary headwords found: ${index.size}`);
console.log(`Headwords with multiple source senses: ${multiple.length}`);
console.log(`Unreviewed suggestions saved to ${output}`);
