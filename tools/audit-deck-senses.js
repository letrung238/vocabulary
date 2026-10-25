#!/usr/bin/env node
/** Audit the canonical vocabulary decks; run from any directory. */
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const sources = ['seed_words.json',
  ...fs.readdirSync(path.join(root, 'decks')).filter(name => name.endsWith('.json')).sort()
    .map(name => `decks/${name}`)];
const read = name => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));
const entries = sources.flatMap(file => read(file).map(item => ({ file, item })));
const byWord = new Map();
for (const entry of entries) {
  const key = entry.item.word?.trim().toLowerCase();
  if (!key) throw new Error(`Word is missing in ${entry.file}`);
  if (!byWord.has(key)) byWord.set(key, []);
  byWord.get(key).push(entry);
}
const valid = item => {
  const main = item.meaningVi?.trim();
  return Boolean(main && Array.isArray(item.senses) && item.senses.some(sense =>
    sense.meaningVi?.trim() && sense.meaningVi.trim().toLowerCase() !== main.toLowerCase()));
};
const missing = entries.filter(({ item }) => !valid(item));
const invalidSenses = [];
for (const { file, item } of entries) {
  if (item.senses === undefined) continue;
  if (!Array.isArray(item.senses)) {
    invalidSenses.push({ file, word: item.word, issue: 'senses must be an array' });
    continue;
  }
  const seen = new Set();
  for (const sense of item.senses) {
    const meaning = sense?.meaningVi?.trim().toLowerCase();
    const pos = sense?.pos?.trim().toLowerCase();
    if (!meaning || !pos) invalidSenses.push({ file, word: item.word, issue: 'empty meaning or part of speech' });
    else if (meaning === item.meaningVi.trim().toLowerCase())
      invalidSenses.push({ file, word: item.word, issue: 'secondary repeats primary' });
    else if (seen.has(`${pos}\0${meaning}`))
      invalidSenses.push({ file, word: item.word, issue: 'duplicate secondary' });
    seen.add(`${pos}\0${meaning}`);
  }
}
const missingUnique = [...byWord].filter(([, copies]) => copies.every(({ item }) => !valid(item)));
const exceptionWords = fs.readFileSync(path.join(__dirname, 'sense-exceptions.txt'), 'utf8')
  .split(/\r?\n/).map(line => line.trim().toLowerCase()).filter(line => line && !line.startsWith('#'));
const exceptions = new Set(exceptionWords);
if (exceptions.size !== exceptionWords.length) throw new Error('Duplicate words in sense-exceptions.txt');
const staleExceptions = [...exceptions].filter(word => !byWord.has(word) ||
  byWord.get(word).some(({ item }) => valid(item)));
const unresolved = missing.filter(({ item }) => !exceptions.has(item.word.toLowerCase()));
const exceptionEntries = missing.filter(({ item }) => exceptions.has(item.word.toLowerCase()));
const crossDeckVariants = [...byWord].filter(([, copies]) => copies.length > 1 &&
  new Set(copies.map(({ item }) => JSON.stringify([item.meaningVi, item.senses ?? []]))).size > 1);
const report = {
  sourceFiles: sources.length,
  entries: entries.length,
  uniqueWords: byWord.size,
  validEntries: entries.length - missing.length,
  exceptionEntries: exceptionEntries.length,
  unresolvedEntries: unresolved.length,
  invalidSenses,
  missingEntries: missing.length,
  missingUniqueWords: missingUnique.length,
  unresolvedUniqueWords: missingUnique.filter(([word]) => !exceptions.has(word)).length,
  staleExceptions,
  crossDeckVariants: crossDeckVariants.map(([word, copies]) => ({ word, files: copies.map(x => x.file) })),
  byFile: sources.map(file => ({ file, total: entries.filter(x => x.file === file).length,
    missing: missing.filter(x => x.file === file).length })),
  missing: missing.map(({ file, item }) => ({ file, word: item.word, main: item.meaningVi }))
};
const localIndex = process.argv.indexOf('--local');
if (localIndex !== -1) {
  const localPath = process.argv[localIndex + 1];
  if (!localPath) throw new Error('--local requires a path to deck.json');
  const data = JSON.parse(fs.readFileSync(localPath, 'utf8'));
  const words = Array.isArray(data) ? data : data.words;
  if (!Array.isArray(words)) throw new Error('Local deck must contain words[]');
  report.local = { total: words.length, complete: words.filter(valid).length,
    missing: words.filter(item => !valid(item)).length,
    outsideCanonical: words.filter(item => !byWord.has(item.word?.trim().toLowerCase())).length };
}
if (process.argv.includes('--json')) console.log(JSON.stringify(report, null, 2));
else {
  console.log(`Decks: ${report.entries} entries, ${report.uniqueWords} distinct words`);
  console.log(`Secondary sense present: ${report.validEntries}/${report.entries}`);
  console.log(`Missing secondary sense: ${report.missingEntries} entries, ${report.missingUniqueWords} distinct words`);
  console.log(`Documented single-sense exceptions: ${report.exceptionEntries}; unresolved: ${report.unresolvedEntries} entries, ${report.unresolvedUniqueWords} distinct words`);
  console.log(`Invalid secondary senses: ${invalidSenses.length}`);
  report.byFile.forEach(({ file, total, missing }) => console.log(`${file}: ${total - missing}/${total} complete`));
  console.log(`Words used with different definitions across decks: ${report.crossDeckVariants.length}; stale exceptions: ${staleExceptions.length}`);
  if (report.local) console.log(`Local deck: ${report.local.complete}/${report.local.total} complete, ${report.local.outsideCanonical} entries outside the repository decks`);
}
if (unresolved.length || invalidSenses.length || staleExceptions.length) process.exitCode = 1;
