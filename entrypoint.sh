#!/bin/sh -l
    
./get-closing-labels.sh -o $INPUT_OWNER -n $INPUT_NAME -p $INPUT_PR_NUMBER | jq \
    --arg ignore "$INPUT_IGNORE" \
    --arg respect_unlabeled "$INPUT_RESPECT_UNLABELED" \
    'def split_ignore: if $ignore == "" then [] else $ignore | split(",") end;
     .closing as $closing |
     .removed as $removed |
     split_ignore as $ignore_split |
     {
       closing: $closing,
       removed: $removed,
       ignore_split: $ignore_split,
       result: (
          if $respect_unlabeled == "true" 
          then $closing - $removed 
          else $closing end 
          - $ignore_split
       )
     } | .result | join(",")'

