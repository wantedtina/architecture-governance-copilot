#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FFMPEG="${FFMPEG:-/tmp/agc-ffmpeg-runtime/node_modules/ffmpeg-static/ffmpeg}"
OUTPUT="${OUTPUT:-$ROOT/video/output/architecture_governance_copilot_draft.mp4}"
SUBTITLE_OUTPUT="${SUBTITLE_OUTPUT:-${OUTPUT%.mp4}.srt}"
SUBTITLE_SOURCE="${SUBTITLE_SOURCE:-$ROOT/video/SUBTITLES_DRAFT.srt}"
NARRATION_AUDIO="${NARRATION_AUDIO:-$ROOT/video/audio/provisional_offline_tts_revised.wav}"
WATERMARK_TEXT="${WATERMARK_TEXT:-DRAFT - PROVISIONAL OFFLINE TTS}"
ARCHITECTURE_DURATION="${ARCHITECTURE_DURATION:-22}"
DEMO_DURATION="${DEMO_DURATION:-136}"
BUSINESS_DURATION="${BUSINESS_DURATION:-18}"
CLOSING_DURATION="${CLOSING_DURATION:-10}"
FONT="/System/Library/Fonts/Supplemental/Arial.ttf"
RECORDING="$ROOT/video/recordings/architecture_governance_copilot_demo_source.webm"

if [[ ! -x "$FFMPEG" ]]; then
  printf 'FFmpeg executable not found: %s\n' "$FFMPEG" >&2
  exit 1
fi

mkdir -p "$ROOT/video/output"

RECORDING_HMS="$({ "$FFMPEG" -i "$RECORDING" 2>&1 || true; } \
  | sed -nE 's/.*Duration: ([0-9]+):([0-9]+):([0-9.]+),.*/\1 \2 \3/p' \
  | head -n 1)"
if [[ -z "$RECORDING_HMS" ]]; then
  printf 'Unable to determine recording duration: %s\n' "$RECORDING" >&2
  exit 1
fi
read -r RECORDING_HOURS RECORDING_MINUTES RECORDING_SECONDS <<<"$RECORDING_HMS"
RECORDING_DURATION="$(awk \
  -v hours="$RECORDING_HOURS" \
  -v minutes="$RECORDING_MINUTES" \
  -v seconds="$RECORDING_SECONDS" \
  'BEGIN { printf "%.6f", (hours * 3600) + (minutes * 60) + seconds }')"
DEMO_STRETCH="$(awk -v duration="$RECORDING_DURATION" -v target="$DEMO_DURATION" \
  'BEGIN { printf "%.9f", target / duration }')"
TOTAL_DURATION="$(awk \
  -v architecture="$ARCHITECTURE_DURATION" \
  -v demo="$DEMO_DURATION" \
  -v business="$BUSINESS_DURATION" \
  -v closing="$CLOSING_DURATION" \
  'BEGIN { printf "%.3f", 11 + 19 + 8 + 14 + architecture + demo + business + closing }')"

"$FFMPEG" -y \
  -loop 1 -framerate 30 -t 11 -i "$ROOT/video/assets/opening-title.png" \
  -loop 1 -framerate 30 -t 19 -i "$ROOT/video/assets/current-process.png" \
  -loop 1 -framerate 30 -t 8 -i "$ROOT/video/assets/current-process.png" \
  -loop 1 -framerate 30 -t 14 -i "$ROOT/video/assets/proposed-solution.png" \
  -loop 1 -framerate 30 -t "$ARCHITECTURE_DURATION" -i "$ROOT/video/assets/architecture-future.png" \
  -i "$RECORDING" \
  -loop 1 -framerate 30 -t "$BUSINESS_DURATION" -i "$ROOT/video/assets/proposed-solution.png" \
  -loop 1 -framerate 30 -t "$CLOSING_DURATION" -i "$ROOT/video/assets/closing-card.png" \
  -i "$NARRATION_AUDIO" \
  -filter_complex "\
    [0:v]scale=1920:1080,format=yuv420p,trim=duration=11,setpts=PTS-STARTPTS[v0];\
    [1:v]scale=1920:1080,format=yuv420p,trim=duration=19,setpts=PTS-STARTPTS[v1];\
    [2:v]scale=1920:1080,format=yuv420p,trim=duration=8,setpts=PTS-STARTPTS[v2];\
    [3:v]scale=1920:1080,format=yuv420p,trim=duration=14,setpts=PTS-STARTPTS[v3];\
    [4:v]scale=1920:1080,format=yuv420p,trim=duration=${ARCHITECTURE_DURATION},setpts=PTS-STARTPTS[v4];\
    [5:v]scale=1920:1080,format=yuv420p,setpts=${DEMO_STRETCH}*(PTS-STARTPTS),fps=30,trim=duration=${DEMO_DURATION}[v5];\
    [6:v]scale=1920:1080,format=yuv420p,trim=duration=${BUSINESS_DURATION},setpts=PTS-STARTPTS[v6];\
    [7:v]scale=1920:1080,format=yuv420p,trim=duration=${CLOSING_DURATION},setpts=PTS-STARTPTS[v7];\
    [v0][v1][v2][v3][v4][v5][v6][v7]concat=n=8:v=1:a=0[base];\
    [base]subtitles='$SUBTITLE_SOURCE':force_style='FontName=Arial,FontSize=12,PrimaryColour=&H00FFFFFF,OutlineColour=&H00061D33,BackColour=&H38061D33,BorderStyle=3,Outline=1,Shadow=0,Alignment=2,MarginV=8',\
    drawtext=fontfile='$FONT':text='$WATERMARK_TEXT':fontcolor=white@0.80:fontsize=22:box=1:boxcolor=0x061D33AA:boxborderw=10:x=w-tw-32:y=28[vout]" \
  -map "[vout]" \
  -map 8:a:0 \
  -c:v libx264 \
  -preset medium \
  -crf 18 \
  -r 30 \
  -pix_fmt yuv420p \
  -c:a aac \
  -b:a 192k \
  -ar 48000 \
  -movflags +faststart \
  -t "$TOTAL_DURATION" \
  "$OUTPUT"

cp "$SUBTITLE_SOURCE" "$SUBTITLE_OUTPUT"
printf '%s\n' "$OUTPUT"
