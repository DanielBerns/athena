#!/bin/bash

# Check if the source directory is provided as a command-line argument
if [ $# -ne 1 ]; then
  echo "Usage: $0 <source_directory>"
  exit 1
fi

SOURCE_DIR="$1"
DEST_DIR="~/Apps/precios_claros" # Destination directory is hardcoded as "B"

# Check if the source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
  echo "Error: Source directory '$SOURCE_DIR' does not exist."
  exit 1
fi

# Create the destination directory if it doesn't exist
if [ ! -d "$DEST_DIR" ]; then
  mkdir -p "$DEST_DIR"
fi

# Copy the source directory to the destination directory
cp -r "$SOURCE_DIR" "$DEST_DIR"

# Check if the copy was successful.
if [ $? -eq 0 ]; then
    echo "Directory '$SOURCE_DIR' copied to '$DEST_DIR' successfully."
    cd "$DEST_DIR"
    git add .
    git commit -m "weekly update '$SOURCE_DIR'"
    git push
else
    echo "Error: Failed to copy directory '$SOURCE_DIR' to '$DEST_DIR'."
    exit 1
fi

exit 0
