#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 -o owner -n name -p pr_number"
    exit
}

# Parse command-line arguments
while getopts ":o:n:p:" opt; do
  case $opt in
    o) owner="$OPTARG"
    ;;
    n) name="$OPTARG"
    ;;
    p) pr_number="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
        usage
    ;;
    :) echo "Option -$OPTARG requires an argument." >&2
       usage
    ;;
  esac
done

# Check if all required arguments are provided
if [ -z "$owner" ] || [ -z "$name" ] || [ -z "$pr_number" ]; then
    usage
fi

response=$(gh api graphql \
    --paginate \
    -F number=$pr_number -F owner=$owner -F name=$name \
    -f query='
    query($endCursor: String, $owner: String!, $name: String!, $number: Int!) {
        repository(owner: $owner, name: $name) {
          pullRequest(number: $number) {
            timelineItems(first: 10, after: $endCursor) {
                nodes {
                    __typename
                    ... on UnlabeledEvent {
                        label {
                            name 
                        }
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
            closingIssuesReferences(first: 10, after: $endCursor) {
              nodes {
                labels(first: 10) {
                  nodes {
                    name
                  }
                }
              }
              pageInfo {
                endCursor
                hasNextPage
              }
            }
          }
        }
    } 
    ' --jq '
        {
            closing: (.data.repository.pullRequest.closingIssuesReferences.nodes
            | map(.labels.nodes | map(.name))
            | flatten
            | unique),
            removed: (.data.repository.pullRequest.timelineItems.nodes
            | map(select(.__typename == "UnlabeledEvent") | .label.name)
            | select(length > 0)
            | unique)
        }
    '
)

echo $response
