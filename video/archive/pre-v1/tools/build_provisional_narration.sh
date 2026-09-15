#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FFMPEG="${FFMPEG:-/tmp/agc-ffmpeg-runtime/node_modules/ffmpeg-static/ffmpeg}"
SEGMENTS="$ROOT/video/audio/provisional_tts_segments"
OUTPUT="$ROOT/video/audio/provisional_offline_tts_revised.wav"

if [[ ! -x "$FFMPEG" ]]; then
  printf 'FFmpeg executable not found: %s\n' "$FFMPEG" >&2
  exit 1
fi

align_segment() {
  local segment="$1"
  local target="$2"
  local text_file="$SEGMENTS/segment_${segment}.txt"
  local source_file="$SEGMENTS/segment_${segment}.aiff"
  local output_file="$SEGMENTS/segment_${segment}_aligned.wav"

  say -v Daniel -o "$source_file" -f "$text_file"

  local source_hms
  source_hms="$({ "$FFMPEG" -i "$source_file" 2>&1 || true; } \
    | sed -nE 's/.*Duration: ([0-9]+):([0-9]+):([0-9.]+),.*/\1 \2 \3/p' \
    | head -n 1)"
  read -r hours minutes seconds <<<"$source_hms"
  local source_duration
  source_duration="$(awk \
    -v hours="$hours" -v minutes="$minutes" -v seconds="$seconds" \
    'BEGIN { printf "%.6f", (hours * 3600) + (minutes * 60) + seconds }')"

  local tempo
  tempo="$(awk -v source="$source_duration" -v target="$target" \
    'BEGIN {
      safe = target - 0.60;
      if (source > safe) printf "%.6f", source / safe;
      else printf "1.000000";
    }')"

  "$FFMPEG" -y -i "$source_file" \
    -af "atempo=${tempo},aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad,atrim=duration=${target},asetpts=N/SR/TB" \
    -c:a pcm_s16le "$output_file" >/dev/null 2>&1
}

align_segment 1 11
align_segment 2 19
align_segment 3 8
align_segment 4 14
align_segment 7 22
align_segment 5 136
align_segment 6 18
align_segment 8 10

"$FFMPEG" -y \
  -i "$SEGMENTS/segment_1_aligned.wav" \
  -i "$SEGMENTS/segment_2_aligned.wav" \
  -i "$SEGMENTS/segment_3_aligned.wav" \
  -i "$SEGMENTS/segment_4_aligned.wav" \
  -i "$SEGMENTS/segment_7_aligned.wav" \
  -i "$SEGMENTS/segment_5_aligned.wav" \
  -i "$SEGMENTS/segment_6_aligned.wav" \
  -i "$SEGMENTS/segment_8_aligned.wav" \
  -filter_complex "[0:a][1:a][2:a][3:a][4:a][5:a][6:a][7:a]concat=n=8:v=0:a=1[out]" \
  -map "[out]" -c:a pcm_s16le "$OUTPUT" >/dev/null 2>&1

printf '%s\n' "$OUTPUT"
