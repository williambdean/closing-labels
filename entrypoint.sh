#!/bin/sh -l

set -e

# These are json arrays
closing=$(get-closing-labels -o $INPUT_OWNER -n $INPUT_REPO -p $INPUT_PR_NUMBER)
removed=$(get-removed-labels -o $INPUT_OWNER -n $INPUT_REPO -p $INPUT_PR_NUMBER)

echo "Closing labels: $closing"
echo "Removed labels: $removed"

echo "{}" | jq \
    --argjson closing "$closing" \
    --argjson removed "$removed" \
    --arg ignore $INPUT_IGNORE \
    --arg respect_unlabeled $INPUT_RESPECT_UNLABELED '

    def split_ignore: 
        if $ignore == "" then
            [] 
        else 
            $ignore | split(",") 
        end;

    def create_result:
        if $respect_unlabeled == "true" then
            $closing - $removed
        else
            $closing
        end;

    split_ignore as $ignore_split |
    create_result as $result |

    { 
        closing: $closing, 
        removed: $removed, 
        ignore: $ignore_split,
        result: ($result - $ignore_split),
    } | .result | join(",")
'
