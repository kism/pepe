#!/bin/bash

# Directory to search
directory="output"

# Find files and read them into an array
readarray -d '' files < <(find "$directory" -type f \( -name "*.png" -o -name "*.mp4" -o -name "*.gif" \) -print0)

# Print the array elements
echo "Found files:"
for file in "${files[@]}"; do
        ffmpeg -v error -i  "$file" -f null -
done
