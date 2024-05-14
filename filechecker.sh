#!/bin/bash

# Directory to search
directory="output"

# Find files and read them into an array
readarray -d '' files < <(find "$directory" -type f \( -name "*.png" -o -name "*.mp4" -o -name "*.gif" \) -print0)

files=($(for i in "${files[@]}"; do echo $i; done | sort)) # Sort

# Print the array elements
echo "Checking files..."
for file in "${files[@]}"; do
    echo
    echo "Checking: $file"
    ffmpeg -v error -i  "$file" -f null -
done
