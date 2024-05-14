#!/bin/bash

# Directory to search
directory="output"

# Find files and read them into an array
files=()
borked_files=()

readarray -d '' files < <(find "$directory" -type f \( -name "*.png" -o -name "*.mp4" -o -name "*.gif" \) -print0)
readarray -t sorted_files < <(printf '%s\n' "${files[@]}" | sort)

# Print the array elements
echo "Checking files..."
for file in "${sorted_files[@]}"; do
    echo
    echo "Checking: $file"
    ffmpeg -v error -i  "$file" -f null -
    if [ $? -ne 0 ]; then
        echo "Adding $file to the borked file list"
        borked_files+=("$file")
    fi
done

echo "List of borked files and the commands to run..."
for file in "${borked_files[@]}"; do
    echo "rm \"$file\""
done
