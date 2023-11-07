#!/bin/bash

# Check if mandatory environment variables are set
if [ -z "$OPENAI_API_KEY" ] || [ -z "$GH_TOKEN" ] || [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ]; then
  echo "Required environment variables are missing."
  exit 1
fi

git config --global --add safe.directory /github/workspace

# Configure Git and GitHub CLI
git config --global user.email "action@github.com"
git config --global user.name "GitHub Action"
gh auth login --with-token <<< "$GH_TOKEN"

# Change directory to the GitHub workspace where the code is checked out
export PYTHONPATH="/usr/src/app:$PYTHONPATH"

cd $GITHUB_WORKSPACE || exit
pwd
echo "Current directory: $(pwd)"
ls -alh

# Fetch the latest main branch into a temporary branch
git fetch origin main:temp-main

# Checkout the temporary main branch
git checkout temp-main

# Create and checkout a new branch for the feature
FEATURE_BRANCH="feature/add-summary-${GITHUB_SHA}"
git checkout -b "$FEATURE_BRANCH"

# Find changed VTT files
files=$(git diff --name-only origin/main...HEAD | grep 'docs_mr/.*\.vtt' | tr '\n' ' ')
echo "Changed VTT files: $files"

# List files before running script
ls -l docs_mr/

#chmod +x minervasmemo.py

# Run Minerva's Memo script for summarization on each VTT file
for file in $files; do
  echo "Processing $file"
  # Directly use the full path to the script and the input file
  python /usr/src/app/minervasmemo.py -i "/github/workspace/docs_mr/$file" --mode summarize >> minervasmemo.log 2>&1
done
ls -l docs_mr/
cat minervasmemo.log

# Read token and cost information
model_info="Model: gpt-3.5-turbo"
token_info=$(cat docs_mr/*_token_info.txt | sed ':a;N;$!ba;s/\n/\\n/g')
info="$model_info\\n$token_info"
echo "Token and Cost Info: $info"

# Commit changes and push to the new branch
git add docs_mr/*.md
if git commit -m "Add cleaned up transcript and summary as markdown"; then
  git push origin "$FEATURE_BRANCH"
  
  # Create Pull Request with the GitHub CLI
  gh pr create --base main --head "$FEATURE_BRANCH" \
    --title "Add cleaned up transcript and summary" \
    --body "$info" \
    --reviewer "$(gh api /repos/:owner/:repo/collaborators | jq -r '.[] | .login')"
else
  echo "No changes to commit"
fi
