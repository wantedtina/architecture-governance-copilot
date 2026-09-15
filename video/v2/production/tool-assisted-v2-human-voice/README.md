# Human voice replacement production

Input video: `/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/tool-assisted-v2/export/architecture-governance-copilot-v2-narrated.mp4`.
Input recordings: `/Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/voice-records/`.

This workspace is separate from V1, V2 and the application. `source/INPUT_MANIFEST.json` hashes original recordings and the original V2 video; `source/PICTURE_MANIFEST.json` hashes copied V2 section clips. No originals were overwritten. Raw audio, recognition output, dependencies and working videos stay outside Git and the submission export.

## Reproduction

`source/replace_voice.py` contains the reviewed caption boundaries, monotonic picture-timing anchors and two-pass loudness normalization. It uses copied V2 section videos, preserving the picture treatment. It repaints the complete old caption band and burns in matching new ASS captions. The section videos are re-encoded once at CRF 17; the final join stream-copies video and encodes the human narration as AAC. Voice speed is never changed. All original recorded samples are included, followed by bounded silence to complete each chapter.

```bash
cd /Users/wantedtina/Repos/architecture-governance-copilot/video/archive/production-originals/tool-assisted-v2-human-voice
python3 source/replace_voice.py
python3 source/verify.py
```

The existing FFmpeg binary path is recorded in `source/v2-runtime.json`. Section filter files and command JSON files record actual render operations. Regenerating the video requires refreshing the export metadata and checksums afterwards. Preserve an accepted human-voice export before making further revisions.

## Local transcription setup

The Remotion captions skill and transcription guidance were read; the Remotion SDK remains unused. A standalone local whisper.cpp CLI supplied word-timing hints, following its upstream documentation: https://github.com/ggml-org/whisper.cpp .

Source was cloned into `tools/whisper.cpp` at commit `f133970bbb8c034ad9055a70afb97d61c24038f9` (reports version 1.9.4-dev). CMake was installed through an isolated `uv run --no-project --with cmake` invocation. CPU/Accelerate build, Metal disabled. The upstream download script fetched the public base.en model into that tool directory. This involved downloading the software/model, not sending recordings to a service. No paid service, account authorization or interactive license-consent step was used. The application environment was not changed.

Build and transcription commands:

```bash
cd tools/whisper.cpp
uv run --no-project --with cmake cmake -B build -DGGML_METAL=OFF -DWHISPER_BUILD_TESTS=OFF -DCMAKE_BUILD_TYPE=Release
uv run --no-project --with cmake cmake --build build --target whisper-cli -j 4 --config Release
sh models/download-ggml-model.sh base.en
cd ../..
python3 source/transcribe.py
```

`source/transcribe.py` runs each recording locally as 16 kHz mono PCM. Recognition output in `qa/` is a timing aid, with known homophone/terminology errors. It does not replace the approved script. Caption bounds were reviewed against actual silence measurements, and final frames were checked at key events. No complete human listening acceptance is claimed.

The exact requested deletion is reflected in the generated story, script and captions. The existing V1/V2 handoffs remain historical records; their pending-human-voice statements are superseded by this completed replacement, subject to user review.
