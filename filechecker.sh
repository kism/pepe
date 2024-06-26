#!/bin/bash

# Directory to search
directory="output"

# Find files and read them into an array
files=()
borked_files=()

echo
echo "-- Checking files for incorrect content type --"
readarray -d '' files < <(find "$directory" -type f \( -name "*.glb" -name "*.png" -o -name "*.mp4" -o -name "*.gif" \) -print0)
readarray -t sorted_files < <(printf '%s\n' "${files[@]}" | sort)
for file in "${sorted_files[@]}"; do
    echo "FILE checking: \"$file\"..."
    if file "$file" | grep -q "text"; then
        echo " Adding \"$file\" to the borked file list"
        borked_files+=("$file")
    else
        echo " Pass!"
    fi
done


if [ "$1" != "--quick" ]; then
    echo
    echo "-- Checking AV files with ffmpeg --"
    readarray -d '' files < <(find "$directory" -type f \( -name "*.png" -o -name "*.mp4" -o -name "*.gif" \) -print0)
    readarray -t sorted_files < <(printf '%s\n' "${files[@]}" | sort)
    for file in "${sorted_files[@]}"; do
        echo "FFMPEG checking: \"$file\"..."
        ffmpeg -v error -i "$file" -f null -
        if [ $? -ne 0 ]; then
            echo " Adding \"$file\" to the borked file list"
            borked_files+=("$file")
        else
            echo " Pass!"
        fi
    done
fi

echo "List of borked files and the commands to run..."
for file in "${borked_files[@]}"; do
    echo "rm \"$file\""
done
