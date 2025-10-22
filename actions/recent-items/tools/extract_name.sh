#!/bin/bash

# Script to extract the "name" key from JSON files, with fallback to "action.description" or "NO DATA"
# Also extracts title and identifier from metadata.json one directory above each log file
# Usage: ./find_logs_json.sh | ./extract_name.sh
# Or: echo "path/to/file.json" | ./extract_name.sh

# Read from stdin and process each line
while IFS= read -r line; do
    # Skip empty lines and non-file lines (like the header messages)
    if [[ -z "$line" || "$line" =~ ^Finding.* || "$line" =~ ^Search.* ]]; then
        continue
    fi
    
    # Check if the file exists
    if [[ ! -f "$line" ]]; then
        echo "NO DATA"
        continue
    fi
    
    # Extract title and identifier from metadata.json one directory above
    metadata_file=$(dirname "$line")/../metadata.json
    title=""
    identifier=""
    
    if [[ -f "$metadata_file" ]]; then
        title=$(jq -r '.title // empty' "$metadata_file" 2>/dev/null)
        identifier=$(jq -r '.identifier // empty' "$metadata_file" 2>/dev/null)
    fi
    
    # Try to extract the "name" key first
    name=$(jq -r '.name // empty' "$line" 2>/dev/null)
    
    if [[ -n "$name" && "$name" != "null" ]]; then
        main_content="$name"
    else
        # Fallback to action.description
        action_desc=$(jq -r '.action.description // empty' "$line" 2>/dev/null)
        
        if [[ -n "$action_desc" && "$action_desc" != "null" ]]; then
            main_content="$action_desc"
        else
            # Final fallback
            main_content="NO DATA"
        fi
    fi
    
    # Format output with title and identifier if available
    if [[ -n "$title" && "$title" != "null" && -n "$identifier" && "$identifier" != "null" ]]; then
        echo "[$identifier] $title | $main_content"
    elif [[ -n "$identifier" && "$identifier" != "null" ]]; then
        echo "[$identifier] | $main_content"
    else
        echo "$main_content"
    fi
done
