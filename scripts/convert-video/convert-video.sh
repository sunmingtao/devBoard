#!/usr/bin/env bash

set -u
shopt -s nullglob nocaseglob

recipient="sunmingtao@gmail.com"
log_file="convert-video-errors.log"
output_dir="output"
summary_file="$(mktemp)"
job_status_dir="$(mktemp -d)"
MAX_JOBS=${MAX_JOBS:-4}
SUBTITLE_FONT=${SUBTITLE_FONT:-Noto Sans CJK SC}
video_patterns=(
  *.3g2 *.3gp *.asf *.avi *.flv *.m4v *.mkv *.mov *.mp4 *.mpeg *.mpg
  *.mts *.m2ts *.ogv *.rm *.rmvb *.ts *.vob *.webm *.wmv
)

declare -a folder_dirs=()
declare -a folder_status_dirs=()

converted=0
failed=0
skipped=0
renamed=0
rename_failed=0
script_start_seconds=$SECONDS

: > "$log_file"
mkdir -p "$output_dir"

send_email() {
  local subject=$1
  local body_file=$2

  if command -v mail >/dev/null 2>&1; then
    mail -s "$subject" "$recipient" < "$body_file"
  elif command -v mailx >/dev/null 2>&1; then
    mailx -s "$subject" "$recipient" < "$body_file"
  elif command -v sendmail >/dev/null 2>&1; then
    {
      printf 'To: %s\n' "$recipient"
      printf 'Subject: %s\n\n' "$subject"
      cat "$body_file"
    } | sendmail "$recipient"
  else
    printf 'No supported mail command found; completion email was not sent.\n' >> "$log_file"
  fi
}

escape_filter_value() {
  local value=$1
  value=${value//\\/\\\\}
  value=${value//\'/\\\'}
  printf "'%s'" "$value"
}

format_duration() {
  local total_seconds=$1
  local hours minutes seconds

  hours=$((total_seconds / 3600))
  minutes=$(((total_seconds % 3600) / 60))
  seconds=$((total_seconds % 60))

  if (( hours > 0 )); then
    printf '%dh %02dm %02ds' "$hours" "$minutes" "$seconds"
  elif (( minutes > 0 )); then
    printf '%dm %02ds' "$minutes" "$seconds"
  else
    printf '%ds' "$seconds"
  fi
}

wait_for_slot() {
  while (( $(jobs -rp | wc -l) >= MAX_JOBS )); do
    sleep 1
  done
}

convert_one() {
  local input_file=$1
  local folder_output_dir=$2
  local status_file=$3
  local file_name base_name output_file
  local subtitle_filter_index chinese_subtitle_filter_index subtitle_stream_number
  local stream_index codec_name language title stream_filter_index title_lower
  local video_filter
  local -a ffmpeg_args

  file_name=${input_file##*/}
  base_name=${file_name%.*}
  output_file="${folder_output_dir}/${base_name}.mp4"

  if [[ -e "$output_file" ]]; then
    printf 'Skipping %s: output %s already exists.\n' "$input_file" "$output_file" >> "$log_file"
    printf 'skipped\n' > "$status_file"
    return
  fi

  if [[ "$input_file" == "$output_file" ]]; then
    printf 'Skipping %s: input and output names are identical.\n' "$input_file" >> "$log_file"
    printf 'skipped\n' > "$status_file"
    return
  fi

  printf 'Converting %s -> %s\n' "$input_file" "$output_file"

  subtitle_filter_index=""
  chinese_subtitle_filter_index=""
  subtitle_stream_number=0
  while IFS='|' read -r stream_index codec_name language title; do
    [[ -n "$stream_index" ]] || continue
    stream_filter_index=$subtitle_stream_number
    ((subtitle_stream_number++))

    codec_name=${codec_name,,}
    case "$codec_name" in
      ass|mov_text|ssa|subrip|text|webvtt) ;;
      *) continue ;;
    esac

    [[ -n "$subtitle_filter_index" ]] || subtitle_filter_index=$stream_filter_index

    language=${language,,}
    title_lower=${title,,}
    if [[ "$language" =~ ^(chi|zho|zh)([-_].*)?$ || "$title_lower" == *chinese* || "$title" == *中文* ]]; then
      [[ -n "$chinese_subtitle_filter_index" ]] || chinese_subtitle_filter_index=$stream_filter_index

      if [[ "$title_lower" == *simplified* || "$title" == *简体* || "$title" == *简中* ]]; then
        subtitle_filter_index=$stream_filter_index
        break
      fi

      subtitle_filter_index=$chinese_subtitle_filter_index
      continue
    fi

    if [[ -z "$subtitle_filter_index" ]]; then
      subtitle_filter_index=$stream_filter_index
    fi
  done < <(ffprobe -v error -select_streams s \
    -show_entries stream=index,codec_name:stream_tags=language,title \
    -of compact=p=0:nk=1 "$input_file" 2>>"$log_file")

  video_filter="scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2"
  if [[ -n "$subtitle_filter_index" ]]; then
    video_filter+=",subtitles=filename=$(escape_filter_value "$input_file"):si=$subtitle_filter_index:force_style='Fontname=$SUBTITLE_FONT,Fontsize=36,Bold=1,Outline=3,Shadow=1,MarginV=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000'"
  fi

  ffmpeg_args=(
    -y -hide_banner -loglevel error -i "$input_file"
    -map '0:v:0' -map '0:a:0?'
    -vf "$video_filter"
    -c:v libx264 -preset ultrafast -b:v 1.5M
    -c:a aac -b:a 128k
  )

  ffmpeg_args+=(-movflags +faststart "$output_file")

  if ffmpeg "${ffmpeg_args[@]}" 2>>"$log_file"; then
    printf 'converted\n' > "$status_file"
  else
    printf 'failed\n' > "$status_file"
    printf 'Failed to convert %s\n' "$input_file" >> "$log_file"
    rm -f "$output_file"
  fi
}

job_number=0
folder_number=0
for source_dir in */; do
  source_dir=${source_dir%/}
  [[ -d "$source_dir" ]] || continue
  [[ "$source_dir" == "$output_dir" || "$source_dir" == *done ]] && continue

  folder_has_videos=0
  status_subdir="$job_status_dir/folder-$folder_number"
  folder_output_dir="$output_dir/$source_dir"

  for pattern in "${video_patterns[@]}"; do
    for input_file in "$source_dir"/$pattern; do
      [[ -f "$input_file" ]] || continue

      if (( folder_has_videos == 0 )); then
        mkdir -p "$status_subdir" "$folder_output_dir"
        folder_dirs+=("$source_dir")
        folder_status_dirs+=("$status_subdir")
        ((folder_number++))
        folder_has_videos=1
      fi

      wait_for_slot
      convert_one "$input_file" "$folder_output_dir" "$status_subdir/job-$job_number.status" &
      ((job_number++))
    done
  done
done

wait

for status_file in "$job_status_dir"/*/*.status; do
  [[ -f "$status_file" ]] || continue

  case "$(<"$status_file")" in
    converted) ((converted++)) ;;
    failed) ((failed++)) ;;
    skipped) ((skipped++)) ;;
  esac
done

for folder_index in "${!folder_dirs[@]}"; do
  source_dir=${folder_dirs[$folder_index]}
  status_subdir=${folder_status_dirs[$folder_index]}
  folder_failed=0

  for status_file in "$status_subdir"/*.status; do
    [[ -f "$status_file" ]] || continue
    if [[ "$(<"$status_file")" == "failed" ]]; then
      folder_failed=1
      break
    fi
  done

  (( folder_failed == 0 )) || continue

  done_dir="${source_dir}-done"
  if [[ -e "$done_dir" ]]; then
    printf 'Not renaming %s: %s already exists.\n' "$source_dir" "$done_dir" >> "$log_file"
    ((rename_failed++))
  elif mv -- "$source_dir" "$done_dir"; then
    ((renamed++))
  else
    printf 'Failed to rename %s to %s.\n' "$source_dir" "$done_dir" >> "$log_file"
    ((rename_failed++))
  fi
done

elapsed_seconds=$((SECONDS - script_start_seconds))
elapsed_time=$(format_duration "$elapsed_seconds")

{
  printf 'Video conversion complete.\n\n'
  printf 'Converted: %d\n' "$converted"
  printf 'Failed: %d\n' "$failed"
  printf 'Skipped: %d\n' "$skipped"
  printf 'Folders renamed: %d\n' "$renamed"
  printf 'Folder rename failures: %d\n' "$rename_failed"
  printf 'Time spent: %s\n' "$elapsed_time"
  printf 'Directory: %s\n' "$PWD"
  if (( failed > 0 || skipped > 0 || rename_failed > 0 )); then
    printf '\nSee %s for details.\n' "$log_file"
  fi
} > "$summary_file"

send_email "Video conversion complete" "$summary_file"
cat "$summary_file"
rm -f "$summary_file"
rm -rf "$job_status_dir"
