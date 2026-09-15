#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FFMPEG="${FFMPEG:-/tmp/agc-ffmpeg-runtime/node_modules/ffmpeg-static/ffmpeg}"
INPUT_DIR="$ROOT/video/human_voice"
SEGMENTS="$ROOT/video/audio/human_voice_segments"
OUTPUT="$ROOT/video/audio/human_voice_narration.wav"

if [[ ! -x "$FFMPEG" ]]; then
  printf 'FFmpeg executable not found: %s\n' "$FFMPEG" >&2
  exit 1
fi

mkdir -p "$SEGMENTS"

prepare_segment() {
  local number="$1"
  local filename="$2"
  local target="$3"
  local input="$INPUT_DIR/$filename"
  local aligned="$SEGMENTS/segment_${number}_aligned.wav"

  if [[ ! -f "$input" ]]; then
    printf 'Human narration file not found: %s\n' "$input" >&2
    exit 1
  fi

  local source_hms
  source_hms="$({ "$FFMPEG" -i "$input" 2>&1 || true; } \
    | sed -nE 's/.*Duration: ([0-9]+):([0-9]+):([0-9.]+),.*/\1 \2 \3/p' \
    | head -n 1)"
  if [[ -z "$source_hms" ]]; then
    printf 'Unable to determine narration duration: %s\n' "$input" >&2
    exit 1
  fi

  local hours minutes seconds
  read -r hours minutes seconds <<<"$source_hms"
  local source_duration
  source_duration="$(awk \
    -v hours="$hours" -v minutes="$minutes" -v seconds="$seconds" \
    'BEGIN { printf "%.6f", (hours * 3600) + (minutes * 60) + seconds }')"

  # Leave a tiny amount of headroom so atrim can only remove generated padding,
  # never recorded speech. Two gentle atempo passes preserve pitch better than
  # one larger pass. No silence removal or content filtering is applied.
  local tempo stage_tempo
  tempo="$(awk -v source="$source_duration" -v target="$target" \
    'BEGIN {
      safe = target - 0.08;
      if (source > safe) printf "%.9f", source / safe;
      else printf "1.000000";
    }')"
  stage_tempo="$(awk -v tempo="$tempo" 'BEGIN { printf "%.9f", sqrt(tempo) }')"

  "$FFMPEG" -y -loglevel error -i "$input" \
    -af "atempo=${stage_tempo},atempo=${stage_tempo},apad,atrim=duration=${target},asetpts=N/SR/TB" \
    -ar 48000 -ac 2 -c:a pcm_s16le "$aligned"

  printf 'segment %s: source %.2fs, target %.2fs, tempo %sx\n' \
    "$number" "$source_duration" "$target" "$tempo"
}

prepare_segment 1 "AGC Opening.m4a" 11
prepare_segment 2 "AGC Current process.m4a" 19
prepare_segment 3 "AGC Pain points.m4a" 8
prepare_segment 4 "AGC Proposed solution.m4a" 14
prepare_segment 7 "AGC target system architecture.m4a" 22
prepare_segment 5 "AGC working POC.m4a" 136
prepare_segment 6 "AGC business value and control.m4a" 18
prepare_segment 8 "AGC Closing.m4a" 10

"$FFMPEG" -y -loglevel error \
  -i "$SEGMENTS/segment_1_aligned.wav" \
  -i "$SEGMENTS/segment_2_aligned.wav" \
  -i "$SEGMENTS/segment_3_aligned.wav" \
  -i "$SEGMENTS/segment_4_aligned.wav" \
  -i "$SEGMENTS/segment_7_aligned.wav" \
  -i "$SEGMENTS/segment_5_aligned.wav" \
  -i "$SEGMENTS/segment_6_aligned.wav" \
  -i "$SEGMENTS/segment_8_aligned.wav" \
  -filter_complex "[0:a][1:a][2:a][3:a][4:a][5:a][6:a][7:a]concat=n=8:v=0:a=1[out]" \
  -map "[out]" -c:a pcm_s16le "$OUTPUT"

printf '%s\n' "$OUTPUT"
