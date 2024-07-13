#!/bin/sh

git filter-branch --env-filter '

OLD_EMAIL="neetilaura.kodali@student.griffith.ie"
CORRECT_NAME="Faraji Ombonya"
CORRECT_EMAIL="farajiombonya@gmail.com"

# Change committer info
if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi

# Change author info
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi

' --tag-name-filter cat -- --branches --tags
