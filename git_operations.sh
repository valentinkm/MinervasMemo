#!/bin/bash

# Check if mandatory environment variables are set
if [ -z "$OPENAI_API_KEY" ] || [ -z "$GH_TOKEN" ] || [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ]; then
  echo "Required environment variables are missing."
  exit 1
fi

# Configure Git and GitHub CLI
git config --global user.email "action@github.com"
git config --global user.name "GitHub Action"
gh auth login --with-token <<< "$GH_TOKEN"

# Change directory to the GitHub workspace where the code is checked out
cd $GITHUB_WORKSPACE || exit

# Find changed VTT files
files=$(git diff-tree --no-commit-id --name-only -r HEAD | grep 'docs_mr/.*\.vtt' | tr '\n' ' ')
echo "Changed VTT files: $files"

# List files before running script
ls -l docs_mr/

# Run Minerva's Memo script for summarization on each VTT file
for file in $files; do
  python minervasmemo.py -i "$file" --mode summarize
done

# Read token and cost information
model_info="Model: gpt-3.5-turbo"
token_info=$(cat docs_mr/*_token_info.txt | sed ':a;N;$!ba;s/\n/\\n/g')
info="$model_info\\n$token_info"
echo "Token and Cost Info: $info"

# Commit changes and push
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
git add docs_mr/*.md
if git commit -m "Add cleaned up transcript and summary as markdown"; then
  git push origin "$BRANCH_NAME"
  # Create Pull Request with the GitHub CLI
  gh pr create --base main --head "$BRANCH_NAME" \
    --title "Add cleaned up transcript and summary" \
    --body "$info"
    --reviewer "$(git rev-parse --short HEAD)"
else
  echo "No changes to commit"
fi

  