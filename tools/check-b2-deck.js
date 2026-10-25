#!/usr/bin/env node
/** Check the B2 deck's import contract and its separation from existing words. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const read = file => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
const deckFile = 'decks/b2-1000.json';
const deck = read(deckFile);

const variants = new Map([
  ['honour', 'honor'], ['mould', 'mold'], ['colour', 'color'],
  ['colourful', 'colorful'], ['centre', 'center'], ['theatre', 'theater'],
  ['programme', 'program'], ['organise', 'organize'], ['analyse', 'analyze'],
  ['offence', 'offense'], ['defence', 'defense'], ['licence', 'license'],
  ['grey', 'gray'], ['catalogue', 'catalog'], ['travelling', 'traveling'],
  ['speciality', 'specialty'], ['enquiry', 'inquiry'], ['litre', 'liter'], ['globalisation', 'globalization'],
  ['humour', 'humor'], ['organisation', 'organization'], ['organiser', 'organizer'],
  ['adviser', 'advisor'], ['modernisation', 'modernization'], ['neighbourhood', 'neighborhood'],
  ['authorise', 'authorize'], ['unauthorised', 'unauthorized'], ['minimise', 'minimize'],
  ['characterise', 'characterize'], ['enquire', 'inquire'], ['favourable', 'favorable'], ['jewellery', 'jewelry'],
]);
const canonical = word => {
  const key = word.normalize('NFC').trim().toLowerCase();
  return variants.get(key) ?? key;
};
const existingFiles = [
  'seed_words.json',
  'decks/it-advanced.json',
  ...fs.readdirSync(path.join(root, 'decks'))
    .filter(name => name.endsWith('.json') && name !== 'b2-1000.json')
    .map(name => `decks/${name}`),
];
const existing = new Map();
for (const file of existingFiles) {
  for (const item of read(file)) existing.set(canonical(item.word), file);
}

assert.equal(deck.length, 1000, 'B2 deck must contain exactly 1,000 words');
const seen = new Set();
for (const item of deck) {
  assert.ok(typeof item.word === 'string' && item.word.trim(), 'Every word needs a headword');
  const key = canonical(item.word);
  assert.ok(!seen.has(key), `Duplicate B2 headword or spelling variant: ${item.word}`);
  assert.ok(!existing.has(key), `${item.word} already exists in ${existing.get(key)}`);
  seen.add(key);
  assert.equal(item.level, 'B2', `${item.word}: wrong level`);
  for (const field of ['ipa', 'pos', 'meaningVi', 'example', 'exampleVi']) {
    assert.ok(typeof item[field] === 'string' && item[field].trim(), `${item.word}: missing ${field}`);
  }
  if (item.senses !== undefined) {
    assert.ok(Array.isArray(item.senses), `${item.word}: senses must be an array`);
    for (const sense of item.senses) {
      assert.ok(sense.pos?.trim() && sense.meaningVi?.trim(), `${item.word}: incomplete secondary sense`);
      assert.ok(sense.example?.trim() && sense.exampleVi?.trim(), `${item.word}: missing bilingual secondary context`);
      assert.notEqual(sense.meaningVi.trim().toLowerCase(), item.meaningVi.trim().toLowerCase(),
        `${item.word}: secondary repeats the main meaning`);
    }
  }
}

for (const file of ['catalog.json']) {
  const entry = read(file).files.find(item => item.url === deckFile);
  assert.ok(entry, `${file} must list the B2 deck`);
  assert.equal(entry.count, deck.length, `${file} has the wrong B2 word count`);
}
console.log(`B2: ${deck.length} unique words, no overlap with ${existing.size} existing words; public catalog matches.`);

const supplementFile = 'decks/b2-daily-work-500.json';
const supplement = read(supplementFile);
assert.equal(supplement.length, 500);
assert.deepEqual(supplement, read('decks/b2-daily-work-500.json'));
const evidence = new Map(read('tools/b2-daily-work-provenance.json').map(r => [r.word, r]));
assert.equal(evidence.size, 500);
const baselineFiles = existingFiles.filter(f => f !== supplementFile).concat(deckFile);
const baseline = new Set(baselineFiles.flatMap(f => read(f).map(w => canonical(w.word))));
const newWords = new Set();
for (const item of supplement) {
  const key = canonical(item.word);
  assert.ok(!baseline.has(key) && !newWords.has(key), `New B2 word repeats a headword/variant: ${item.word}`);
  newWords.add(key);
  assert.equal(item.level, 'B2');
  assert.ok(item.tags.includes('b2-daily-work') && item.topic);
  const proof = evidence.get(item.word);
  assert.ok(proof?.ipaReviewed && proof.levelEvidence.some(e => e.level === 'B2'));
  assert.equal(item.ipa, proof.ipa);
  const meanings = new Set();
  for (const sense of [item, ...(item.senses ?? [])]) {
    for (const field of ['ipa', 'pos', 'meaningVi', 'example', 'exampleVi']) assert.ok(sense[field]?.trim(), `${item.word}: ${field}`);
    assert.ok(sense.ipa.startsWith('/') && sense.ipa.endsWith('/'), item.word);
    const identity = `${sense.pos}\0${sense.meaningVi}`;
    assert.ok(!meanings.has(identity)); meanings.add(identity);
  }
}
assert.equal(supplement.filter(w => w.senses?.length).length, 264);
assert.equal(supplement.reduce((n, w) => n + (w.senses?.length ?? 0), 0), 331);
for (const file of ['catalog.json']) assert.equal(read(file).files.find(e => e.url === supplementFile)?.count, 500);
console.log(`B2 daily/work: 500 new words, 331 secondary meanings, ${baseline.size} prior distinct words; no overlaps or spelling variants.`);

const extraFile = 'decks/daily-work-498.json';
const extra = read(extraFile);
const extraProof = new Map(read('tools/daily-work-498-provenance.json').map(r => [r.word, r]));
assert.equal(extra.length, 498);
assert.equal(extraProof.size, 498);
assert.deepEqual(extra, read('decks/daily-work-498.json'));
const priorIds = new Set(existingFiles.filter(f => f !== extraFile).concat(deckFile).flatMap(f => read(f).map(w => canonical(w.word))));
const extraIds = new Set();
for (const item of extra) {
  const key = canonical(item.word);
  assert.ok(!priorIds.has(key) && !extraIds.has(key), `Repeated intermediate headword/variant: ${item.word}`);
  assert.ok(!['work', 'book', 'make', 'get', 'have', 'do', 'eat', 'drink', 'buy', 'see', 'count', 'print'].includes(item.word));
  extraIds.add(key);
  const proof = extraProof.get(item.word);
  assert.ok(proof?.ipaReviewed && proof.level === item.level && proof.primaryPos === item.pos);
  assert.ok(['B1', 'B2'].includes(item.level));
  assert.ok(proof.levelEvidence.some(e => e.level === item.level && e.pos === item.pos));
  assert.equal(item.ipa, proof.ipa);
  assert.ok(item.tags.includes('daily-work-498'));
  for (const sense of [item, ...(item.senses ?? [])]) {
    for (const field of ['pos', 'ipa', 'meaningVi', 'example', 'exampleVi']) assert.ok(sense[field]?.trim(), `${item.word}: missing ${field}`);
  }
}
assert.equal(extra.filter(w => w.senses?.length).length, 227);
assert.equal(extra.reduce((n, w) => n + (w.senses?.length ?? 0), 0), 320);
for (const file of ['catalog.json']) assert.equal(read(file).files.find(e => e.url === extraFile)?.count, 498);
const core = read('seed_words.json').concat(deck, supplement, extra);
assert.equal(core.length, 3000);
assert.equal(new Set(core.map(w => canonical(w.word))).size, 3000);
const sources = read('catalog.json').files;
const catalogRoots = new Set(sources.flatMap(entry => read(entry.url).map(word => canonical(word.word))));
assert.deepEqual(new Set([...priorIds, ...extraIds]), catalogRoots, 'Prior and new roots must cover the current public catalog');
console.log(`Daily/work: 498 novel intermediate words; core selection exactly 3000 distinct words; current catalog ${catalogRoots.size} normalized roots.`);
