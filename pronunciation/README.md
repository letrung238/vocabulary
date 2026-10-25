# Offline English pronunciation

`en-us.tsv.gzip` contains 125,927 General American surface forms and IPA readings
from [open-dict-data/ipa-dict](https://github.com/open-dict-data/ipa-dict),
`data/en_US.txt`, downloaded 2026-10-02. The source is distributed under the MIT
license; the full notice is in `LICENSE.txt`, bundled with both apps.

Source SHA-256: `2af6f154a5c363275f052d1f85acedef38ed185ca9745aa4314be77f6b70de67`.
The only transformations are lowercasing headwords, normalizing curly apostrophes,
sorting and gzip compression. The `.gzip` suffix keeps Android packaging from
automatically expanding the compressed asset. Rebuild with:

```powershell
python tools/build-pronunciation-lexicon.py path/to/en_US.txt
```

Windows and Android load the asset once, on a background thread when a word is
selected. Lookup uses the exact spelling, including inflections and contractions.
An exact deck entry supplies IPA only when the lexicon has no entry. Unknown
words show a missing-IPA message and remain available for text-to-speech.
Multiple readings are preserved (e.g. `read`); the UI does not infer grammatical
context or force a single pronunciation. IPA is a dictionary pronunciation;
the device's installed English voice may use a different accent. No network
dictionary request is sent when a word is clicked.
