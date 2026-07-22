#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FFMPEG="${FFMPEG:-/tmp/agc-ffmpeg-runtime/node_modules/ffmpeg-static/ffmpeg}"
OUTPUT="$ROOT/video/output/architecture_governance_copilot_draft.mp4"
SUBTITLE_OUTPUT="$ROOT/video/output/architecture_governance_copilot_draft.srt"
FONT="/System/Library/Fonts/Supplemental/Arial.ttf"

if [[ ! -x "$FFMPEG" ]]; then
  printf 'FFmpeg executable not found: %s\n' "$FFMPEG" >&2
  exit 1
fi

mkdir -p "$ROOT/video/output"

"$FFMPEG" -y \
  -loop 1 -framerate 30 -t 12 -i "$ROOT/video/assets/opening-title.png" \
  -loop 1 -framerate 30 -t 24 -i "$ROOT/video/assets/current-process.png" \
  -loop 1 -framerate 30 -t 8 -i "$ROOT/video/assets/current-process.png" \
  -loop 1 -framerate 30 -t 8 -i "$ROOT/video/assets/proposed-solution.png" \
  -loop 1 -framerate 30 -t 12 -i "$ROOT/video/assets/architecture-future.png" \
  -i "$ROOT/video/recordings/architecture_governance_copilot_demo_source.webm" \
  -loop 1 -framerate 30 -t 16 -i "$ROOT/video/assets/proposed-solution.png" \
  -loop 1 -framerate 30 -t 7 -i "$ROOT/video/assets/closing-card.png" \
  -i "$ROOT/video/audio/provisional_offline_tts_revised.wav" \
  -filter_complex "\
    [0:v]scale=1920:1080,format=yuv420p,trim=duration=12,setpts=PTS-STARTPTS[v0];\
    [1:v]scale=1920:1080,format=yuv420p,trim=duration=24,setpts=PTS-STARTPTS[v1];\
    [2:v]scale=1920:1080,format=yuv420p,trim=duration=8,setpts=PTS-STARTPTS[v2];\
    [3:v]scale=1920:1080,format=yuv420p,trim=duration=8,setpts=PTS-STARTPTS[v3];\
    [4:v]scale=1920:1080,format=yuv420p,trim=duration=12,setpts=PTS-STARTPTS[v4];\
    [5:v]scale=1920:1080,format=yuv420p,split=3[v5pre_src][v5hold_src][v5post_src];\
    [v5pre_src]trim=end=2.24,setpts=PTS-STARTPTS[v5pre];\
    [v5hold_src]trim=start=2.20:end=2.24,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration=0.12[v5hold];\
    [v5post_src]trim=start=2.40,setpts=PTS-STARTPTS[v5post];\
    [v5pre][v5hold][v5post]concat=n=3:v=1:a=0,setpts=1.06433*(PTS-STARTPTS),fps=30,trim=duration=135[v5];\
    [6:v]scale=1920:1080,format=yuv420p,trim=duration=16,setpts=PTS-STARTPTS[v6];\
    [7:v]scale=1920:1080,format=yuv420p,trim=duration=7,setpts=PTS-STARTPTS[v7];\
    [v0][v1][v2][v3][v4][v5][v6][v7]concat=n=8:v=1:a=0[base];\
    [base]subtitles='$ROOT/video/SUBTITLES_DRAFT.srt':force_style='FontName=Arial,FontSize=12,PrimaryColour=&H00FFFFFF,OutlineColour=&H00061D33,BackColour=&H38061D33,BorderStyle=3,Outline=1,Shadow=0,Alignment=2,MarginV=8',\
    drawtext=fontfile='$FONT':text='DRAFT - PROVISIONAL OFFLINE TTS':fontcolor=white@0.80:fontsize=22:box=1:boxcolor=0x061D33AA:boxborderw=10:x=w-tw-32:y=28[vout]" \
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
  -t 222 \
  "$OUTPUT"

cp "$ROOT/video/SUBTITLES_DRAFT.srt" "$SUBTITLE_OUTPUT"
printf '%s\n' "$OUTPUT"
