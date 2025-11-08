#!/bin/bash

for f in *.m4a; do
    # Get total duration of the file
    duration=$(ffprobe -i "$f" -show_entries format=duration -v quiet -of csv="p=0")

    # Ensure the file is long enough to trim
    if (( $(echo "$duration < 5" | bc -l) )); then
        echo "Skipping $f (too short to trim)"
        continue
    fi

    # Calculate new duration: subtract 4s from start and 0.5s from end
    new_duration=$(echo "$duration - 4.4 - 4.6" | bc)

    # Re-encode properly to avoid playback issues
    ffmpeg -y -i "$f" -ss 4.4 -t "$new_duration" -c:a aac -b:a 192k -strict -2 -movflags +faststart "trimmed_${f%.*}.m4a"
done
