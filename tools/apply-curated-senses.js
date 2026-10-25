#!/usr/bin/env node
/** Apply individually edited secondary uses across every canonical deck. */
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const curationFile = path.join(__dirname, 'curated-secondary-senses.tsv');
const rejectedFile = path.join(__dirname, 'rejected-secondary-senses.tsv');
const skipsFile = path.join(__dirname, 'curated-sense-skips.tsv');
const splitsFile = path.join(__dirname, 'primary-sense-splits.tsv');
const awlSplitsFile = path.join(__dirname, 'awl-primary-sense-splits.tsv');
const rows = fs.readFileSync(curationFile, 'utf8').trim().split(/\r?\n/);
if (rows.shift() !== 'word\tpos\tmeaningVi') throw new Error('Unexpected curation header');
const curated = new Map();
const rejected = new Map();
const skips = new Map();
const splits = new Map();
for (const [file, splitFile] of [['seed_words.json', splitsFile],
  ['decks/ielts-academic.json', awlSplitsFile]]) {
  for (const [index, row] of fs.readFileSync(splitFile, 'utf8').trim().split(/\r?\n/).slice(1).entries()) {
    const cells = row.split('\t');
    if (cells.length !== 5 || cells.some(cell => !cell.trim())) throw new Error(`Invalid primary split row ${index + 2}`);
    const [word, oldMain, newMain, pos, secondaryMeaningVi] = cells;
    const key = `${file}\0${word.toLowerCase()}`;
    if (splits.has(key)) throw new Error(`Duplicate primary split: ${word}`);
    splits.set(key, { oldMain, newMain, pos, secondaryMeaningVi });
  }
}
for (const [index, row] of fs.readFileSync(skipsFile, 'utf8').trim().split(/\r?\n/).slice(1).entries()) {
  const cells = row.split('\t');
  if (cells.length !== 3 || cells.some(cell => !cell.trim())) throw new Error(`Invalid skip row ${index + 2}`);
  const [word, file, meaningVi] = cells;
  const key = `${word.toLowerCase()}\0${file}`;
  if (!skips.has(key)) skips.set(key, new Set());
  skips.get(key).add(meaningVi);
}
for (const [index, row] of fs.readFileSync(rejectedFile, 'utf8').trim().split(/\r?\n/).slice(1).entries()) {
  const cells = row.split('\t');
  if (cells.length !== 2 || cells.some(cell => !cell.trim())) throw new Error(`Invalid rejection row ${index + 2}`);
  const [word, meaningVi] = cells;
  if (!rejected.has(word.toLowerCase())) rejected.set(word.toLowerCase(), new Set());
  rejected.get(word.toLowerCase()).add(meaningVi);
}
for (const [index, row] of rows.entries()) {
  const cells = row.split('\t');
  if (cells.length !== 3 || cells.some(cell => !cell.trim())) throw new Error(`Invalid row ${index + 2}`);
  const [word, pos, meaningVi] = cells;
  const key = word.toLowerCase();
  if (!curated.has(key)) curated.set(key, []);
  if (curated.get(key).some(value => value.pos === pos && value.meaningVi === meaningVi))
    throw new Error(`Duplicate curation: ${word}: ${meaningVi}`);
  curated.get(key).push({ pos, meaningVi });
}
const sourceFiles = ['seed_words.json', ...fs.readdirSync(path.join(root, 'decks'))
  .filter(file => file.endsWith('.json')).sort().map(file => `decks/${file}`)];
const seen = new Set();
const seenSplits = new Set();
const changes = [];
const pending = [];
for (const file of sourceFiles) {
  const absolute = path.join(root, file);
  const original = fs.readFileSync(absolute, 'utf8');
  const data = JSON.parse(original);
  let count = 0;
  for (const item of data) {
    const key = item.word.toLowerCase();
    const splitKey = `${file}\0${key}`;
    const split = splits.get(splitKey);
    if (split) {
      seenSplits.add(splitKey);
      if (item.meaningVi !== split.oldMain && item.meaningVi !== split.newMain)
        throw new Error(`Unexpected primary meaning for ${item.word}: ${item.meaningVi}`);
      if (item.meaningVi === split.oldMain) { item.meaningVi = split.newMain; count++; }
      if (!(item.senses ?? []).some(sense => sense.meaningVi === split.secondaryMeaningVi)) {
        item.senses = [...(item.senses ?? []), { pos: split.pos, meaningVi: split.secondaryMeaningVi }];
        count++;
      }
    }
    const removed = rejected.get(key);
    const skipped = skips.get(`${key}\0${file}`);
    if ((removed || skipped) && item.senses?.length) {
      const kept = item.senses.filter(sense => !removed?.has(sense.meaningVi) && !skipped?.has(sense.meaningVi));
      count += item.senses.length - kept.length;
      if (kept.length) item.senses = kept;
      else delete item.senses;
    }
    const senses = curated.get(key);
    if (!senses) continue;
    seen.add(key);
    const main = item.meaningVi.trim().toLowerCase();
    const additions = senses.filter(sense => !skipped?.has(sense.meaningVi) &&
      sense.meaningVi.trim().toLowerCase() !== main &&
      !(item.senses ?? []).some(value => value.pos === sense.pos && value.meaningVi === sense.meaningVi));
    if (!additions.length) continue;
    item.senses = [...(item.senses ?? []), ...additions];
    count += additions.length;
  }
  if (!count) continue;
  const newline = original.includes('\r\n') ? '\r\n' : '\n';
  const indent = /^\[\r?\n( +)\{/.exec(original)?.[1].length ?? 2;
  pending.push({ file, text: JSON.stringify(data, null, indent).replace(/\n/g, newline) + newline });
  changes.push(`${file}: ${count}`);
}
const unused = [...curated.keys()].filter(key => !seen.has(key));
if (unused.length) throw new Error(`Unknown headwords: ${unused.join(', ')}`);
const unusedSplits = [...splits.keys()].filter(key => !seenSplits.has(key));
if (unusedSplits.length) throw new Error(`Unknown primary splits: ${unusedSplits.join(', ')}`);
if (process.argv.includes('--write')) {
  for (const { file, text } of pending) fs.writeFileSync(path.join(root, file), text);

}
console.log(`${curated.size} curated headwords; ${changes.join(', ') || 'no changes'}`);
console.log(process.argv.includes('--write') ? 'Public canonical decks updated.' : 'Dry run; use --write to apply.');
