#!/usr/bin/env node
/**
 * Gợi ý IPA theo quy ước của bộ seed (kiểu Cambridge, Anh-Anh, có dấu ngắt âm tiết)
 * cho một danh sách từ mới.
 *
 * Chạy:
 *   node tools/ipa-suggest.js <thư-mục-ipa-dict> <file-từ.txt|->   # gợi ý
 *   node tools/ipa-suggest.js <thư-mục-ipa-dict> --selftest        # đo độ chính xác
 *
 * VÌ SAO CÓ FILE NÀY. Viết tay vài trăm dòng IPA thì sai sót là chuyện chắc chắn, mà
 * check-ipa.js chỉ bắt được lỗi định dạng, trùng lặp và lệch trọng âm — nó không đọc hộ.
 * Script này đi đường ngược lại: lấy IPA của ipa-dict (sinh bằng eSpeak-NG) rồi **quy đổi
 * về quy ước của bộ seed**, còn người thì soi phần nó không chắc.
 *
 * NÓ KHÔNG PHẢI CHÂN LÝ. eSpeak là bộ tổng hợp giọng nói, không phải từ điển: nó dùng
 * ɹ/ɐ/ɫ, không ngắt âm tiết, đặt dấu trọng âm ngay trước nguyên âm thay vì đầu âm tiết,
 * và chọn nhầm từ loại ở các cặp đồng tự (moderate, deliberate, lead, refuse). Vì vậy
 * mỗi dòng ra đều kèm **cờ tin cậy**, và `--selftest` đo thẳng tỉ lệ khớp trên 1002 mục
 * đã soát tay của bộ seed để biết con số thật thay vì đoán.
 */
const fs = require('fs');
const path = require('path');

const dictDir = process.argv[2];
const target = process.argv[3];

if (!dictDir) {
  console.error('Thiếu thư mục ipa-dict. Xem chú thích đầu file.');
  process.exit(2);
}

// ---------- nạp từ điển ----------

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
const UK = loadDict('en_UK.txt');
const US = loadDict('en_US.txt');

// ---------- bộ âm vị ----------

/** Nguyên âm đôi phải nhận trước nguyên âm đơn, nếu không /aɪ/ bị cắt thành /a/ + /ɪ/. */
const DIPHTHONGS = ['eɪ', 'aɪ', 'ɔɪ', 'əʊ', 'aʊ', 'ɪə', 'eə', 'ʊə'];
const LONG_VOWELS = ['iː', 'ɑː', 'ɔː', 'uː', 'ɜː'];
const SHORT_VOWELS = ['ɪ', 'e', 'æ', 'ʌ', 'ɒ', 'ʊ', 'ə', 'i', 'u'];
const VOWELS = [...DIPHTHONGS, ...LONG_VOWELS, ...SHORT_VOWELS];

/** Phụ âm đôi cũng phải nhận trước phụ âm đơn. */
const CONSONANTS = [
  'tʃ', 'dʒ', 'θ', 'ð', 'ʃ', 'ʒ', 'ŋ',
  'p', 'b', 't', 'd', 'k', 'ɡ', 'g', 'f', 'v', 's', 'z', 'h', 'm', 'n', 'l', 'r', 'w', 'j'
];

/** Cụm phụ âm đầu âm tiết hợp lệ trong tiếng Anh. Dùng cho nguyên tắc onset tối đa. */
const VALID_ONSETS = new Set([
  'pr', 'br', 'tr', 'dr', 'kr', 'ɡr', 'fr', 'θr', 'ʃr',
  'pl', 'bl', 'kl', 'ɡl', 'fl', 'sl',
  'pj', 'bj', 'kj', 'ɡj', 'fj', 'vj', 'mj', 'nj', 'hj', 'lj', 'tj', 'dj', 'θj', 'sj',
  'tw', 'dw', 'kw', 'ɡw', 'sw', 'θw', 'hw',
  'sp', 'st', 'sk', 'sm', 'sn', 'sf',
  'spr', 'str', 'skr', 'spl', 'skw', 'spj', 'stj', 'skj',
  'ʃt', 'ʃp', 'ʃn', 'ʃv',
]);

// ---------- quy đổi eSpeak -> quy ước seed ----------

/**
 * Quy đổi ký hiệu. Thứ tự quan trọng: thay ɹ trước khi xét cụm, thay ɝ/ɚ trước khi
 * đụng tới ɜ/ə lẻ.
 */
function normalizeSymbols(raw) {
  let s = raw.replace(/[\/\[\]]/g, '').trim();
  s = s
    .replace(/ɹ/g, 'r')
    .replace(/ɫ/g, 'l')
    .replace(/ᵻ/g, 'ɪ')
    .replace(/ɝ/g, 'ɜːr')
    .replace(/ɚ/g, 'ər')
    .replace(/ɐ/g, 'ə')
    .replace(/ɡ/g, 'ɡ')
    .replace(/g/g, 'ɡ')
    .replace(/oʊ/g, 'əʊ')
    .replace(/ɑ(?!ː)/g, 'ɑː')
    .replace(/ɔ(?![ːɪ])/g, 'ɔː')
    .replace(/ɛ/g, 'e')
    .replace(/ɜ(?!ː)/g, 'ɜː');
  // Phi-rhotic: en_UK của ipa-dict vẫn lẫn một số mục kiểu Anh-Mỹ (/ˈɑɹtəˌfækt/). Chữ r
  // không đứng trước nguyên âm thì bỏ; r nối cuối từ do restoreLinkingR dựng lại sau.
  //
  // Lookahead phải nhảy qua dấu trọng âm. eSpeak đặt dấu ngay trước nguyên âm chứ không
  // phải đầu âm tiết, nên trong /əɡɹˈɛsɪv/ chữ r đứng trước `ˈ` — bỏ qua chi tiết đó là
  // xoá mất r trong cụm đầu âm tiết và biến aggressive thành /əˈɡes.ɪv/.
  s = s.replace(/r(?![ˈˌ]*[iɪeɛæaɑɒɔoʊuʌəɜ])/g, '');
  // Trước một nguyên âm khác, /iː/ và /uː/ rút thành /i/ /u/ không thành âm tiết, và /ɪ/
  // thành /i/: /əˈpriː.ʃi.eɪt/ chứ không phải /ʃɪ.eɪt/, /æmˈbɪɡ.ju.əs/ chứ không phải /juː.əs/.
  s = s.replace(/([iu])ː(?=[ˈˌ]*[iɪeɛæaɑɒɔoʊuʌəɜ])/g, '$1');
  // Không được đụng tới ɪ đang là **vế sau của nguyên âm đôi** (aɪ, eɪ, ɔɪ): biến nó
  // thành i sẽ xé /ˈvaɪ.ə/ thành /ˈvai.ə/ và /ˈleɪ.ər/ thành /ˈle.i.ər/.
  s = s.replace(/(?<![aeɔ])ɪ(?=[ˈˌ]*[eɛæaɑɒɔoʊuʌəɜ])/g, 'i');
  return s;
}

/**
 * Bỏ trọng âm phụ đứng **sau** trọng âm chính. eSpeak rắc ˌ lên đuôi -ate/-ize
 * (/ˈæb.ˌstrækt/), từ điển Cambridge thì không. Trọng âm phụ đứng *trước* trọng âm chính
 * là thật và phải giữ: /ˌæk.wɪˈzɪʃ.ən/.
 */
function dropTrailingSecondary(s) {
  const primary = s.indexOf('ˈ');
  if (primary < 0) return s;
  return s.slice(0, primary + 1) + s.slice(primary + 1).replace(/ˌ/g, '');
}

/** Tách chuỗi âm vị thành mảng {sym, stress}. Dấu trọng âm gắn vào âm vị đứng ngay sau. */
function tokenize(s) {
  const out = [];
  let i = 0;
  let pendingStress = '';
  while (i < s.length) {
    const c = s[i];
    if (c === 'ˈ' || c === 'ˌ') { pendingStress = c; i++; continue; }
    if (c === '.' || c === ' ') { i++; continue; }
    let matched = null;
    for (const sym of [...DIPHTHONGS, ...LONG_VOWELS, ...CONSONANTS, ...SHORT_VOWELS]) {
      if (s.startsWith(sym, i)) { matched = sym; break; }
    }
    if (!matched) { matched = c; }
    out.push({ sym: matched, vowel: VOWELS.includes(matched), stress: pendingStress });
    pendingStress = '';
    i += matched.length;
  }
  return out;
}

/**
 * Cắt âm tiết theo nguyên tắc onset tối đa: cụm phụ âm giữa hai nguyên âm dồn về âm tiết
 * sau, miễn là cụm đó mở đầu được một từ tiếng Anh. Đây là quy ước từ điển Cambridge dùng.
 */
function syllabify(tokens) {
  const vowelAt = tokens.map((t, i) => (t.vowel ? i : -1)).filter(i => i >= 0);
  if (vowelAt.length <= 1) return [tokens];

  const syllables = [];
  let start = 0;
  for (let v = 0; v < vowelAt.length - 1; v++) {
    const here = vowelAt[v];
    const next = vowelAt[v + 1];
    const cluster = tokens.slice(here + 1, next);
    // Bao nhiêu phụ âm dồn được sang âm tiết sau?
    let onsetSize = 0;
    for (let take = Math.min(cluster.length, 3); take >= 1; take--) {
      const cand = cluster.slice(cluster.length - take).map(t => t.sym).join('');
      if (take === 1 || VALID_ONSETS.has(cand)) { onsetSize = take; break; }
    }
    if (cluster.length === 0) onsetSize = 0;
    // Quy ước Cambridge: âm tiết mang trọng âm mà nguyên âm NGẮN thì "hút" một phụ âm
    // sau về làm âm cuối — /ˈæk.jə.rət/ chứ không phải /ˈæ.kjʊ.rət/. Nguyên âm dài và
    // nguyên âm đôi thì không: /əˈpriː.ʃi.eɪt/ giữ nguyên ʃ ở đầu âm tiết sau.
    const hereTok = tokens[here];
    const hereStressed = tokens.slice(start, here + 1).some(t => t.stress);
    if (hereStressed && SHORT_VOWELS.includes(hereTok.sym) && onsetSize === cluster.length
        && cluster.length >= 1) {
      onsetSize = Math.max(onsetSize - 1, 0);
    }
    const cut = next - onsetSize;
    syllables.push(tokens.slice(start, cut));
    start = cut;
  }
  syllables.push(tokens.slice(start));
  return syllables.filter(s => s.length);
}

/** Dựng lại chuỗi, dấu trọng âm dời về **đầu âm tiết** như quy ước Cambridge. */
function render(syllables) {
  const parts = syllables.map(syl => {
    const stress = syl.find(t => t.stress)?.stress || '';
    return stress + syl.map(t => t.sym).join('');
  });
  // Bản thân dấu trọng âm đã là ranh giới âm tiết, nên không đặt dấu chấm ngay trước nó:
  // /əbˈzɔːb/ chứ không phải /əb.ˈzɔːb/.
  return parts.reduce((acc, part, i) =>
    i === 0 ? part : acc + (/^[ˈˌ]/.test(part) ? '' : '.') + part, '');
}

/**
 * Khôi phục "r nối" cuối từ. Bộ seed theo lối phi-rhotic có r nối: `eager` là /ˈiː.ɡər/
 * chứ không phải /ˈiː.ɡə/. eSpeak bỏ mất chữ r đó, nên phải suy lại từ mặt chữ.
 */
function restoreLinkingR(ipa, word) {
  if (!/r|re$/i.test(word)) return ipa;
  if (!/(er|or|ar|ur|ir|yr|re|our|eur)$/i.test(word)) return ipa;
  if (/r$/.test(ipa)) return ipa;
  if (/(ə|ɔː|ɑː|ɜː|ʊə|ɪə|eə|iː|uː)$/.test(ipa)) return ipa + 'r';
  return ipa;
}

function suggest(word) {
  const key = word.toLowerCase().trim();
  const raw = UK.get(key) || US.get(key);
  if (!raw) return null;
  const flags = [];
  if (!UK.has(key) && US.has(key)) flags.push('chỉ-có-Anh-Mỹ');
  if (/[ˌ]/.test(raw)) flags.push('có-trọng-âm-phụ');
  const normalized = dropTrailingSecondary(normalizeSymbols(raw));
  const tokens = tokenize(normalized);
  const syllables = syllabify(tokens);
  let out = render(syllables);
  out = restoreLinkingR(out, key);
  // Từ đơn âm tiết không mang dấu trọng âm: bộ seed viết /bætʃ/ chứ không phải /ˈbætʃ/.
  // eSpeak thì đánh dấu mọi từ, kể cả từ một âm tiết.
  if (syllables.length === 1) out = out.replace(/[ˈˌ]/g, '');
  return { ipa: '/' + out + '/', raw, flags };
}

// ---------- tự kiểm trên bộ seed đã soát tay ----------

if (target === '--selftest') {
  const SEED = path.join(__dirname, '..', 'seed_words.json');
  const words = JSON.parse(fs.readFileSync(SEED, 'utf8'));
  let exact = 0, near = 0, off = 0, missing = 0, total = 0;
  const wrong = [];
  for (const w of words) {
    if (w.word.includes(' ') || w.word.includes('-')) continue;
    const s = suggest(w.word);
    if (!s) { missing++; continue; }
    total++;
    if (s.ipa === w.ipa) exact++;
    else {
      // Bỏ dấu ngắt âm tiết ra so: đúng âm vị + đúng trọng âm là đã dùng được.
      const a = s.ipa.replace(/\./g, ''), b = w.ipa.replace(/\./g, '');
      if (a === b) near++;
      else { off++; wrong.push(`${w.word}: gợi ý ${s.ipa}  |  seed ${w.ipa}`); }
    }
  }
  const pct = n => ((n / total) * 100).toFixed(1) + '%';
  console.log('đối chiếu được       :', total, '(không tra được:', missing + ')');
  console.log('khớp tuyệt đối       :', exact, pct(exact));
  console.log('chỉ lệch dấu ngắt    :', near, pct(near));
  console.log('lệch âm vị/trọng âm  :', off, pct(off));
  console.log('\n30 mục lệch đầu tiên:');
  wrong.slice(0, 30).forEach(s => console.log('   - ' + s));
  process.exit(0);
}

// ---------- gợi ý cho danh sách từ ----------

const input = target === '-' || !target
  ? fs.readFileSync(0, 'utf8')
  : fs.readFileSync(target, 'utf8');

for (const line of input.split('\n')) {
  const word = line.trim();
  if (!word) continue;
  const s = suggest(word);
  if (!s) { console.log(`${word}\t\tKHÔNG-TRA-ĐƯỢC`); continue; }
  console.log(`${word}\t${s.ipa}\t${s.flags.join(',')}`);
}
