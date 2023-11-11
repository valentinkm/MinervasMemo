#!/bin/bash
echo "Starting git_operations.sh script"


# Check if mandatory environment variables are set
if [ -z "$OPENAI_API_KEY" ] || [ -z "$GH_TOKEN" ] || [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ]; then
  echo "Required environment variables are missing."
  exit 1
fi

# Allow git to access the GitHub workspace
git config --global --add safe.directory /github/workspace

# Configure Git and GitHub CLI
git config --global user.email "action@github.com"
git config --global user.name "GitHub Action"
gh auth login --with-token <<< "$GH_TOKEN"

# Change directory to the GitHub workspace where the code is checked out
export PYTHONPATH="/usr/src/app:$PYTHONPATH"

 # Change directory to the GitHub workspace where the code is checked out
cd $GITHUB_WORKSPACE || exit
pwd
echo "Current directory: $(pwd)"
ls -alh

# sanity checks
echo "Contents of docs_mr/ directory:" 
ls -alh docs_mr/
echo "The current branch is:"
git branch
echo "GITHUB_REF: ${GITHUB_REF}"
echo "GITHUB_SHA: ${GITHUB_SHA}"

# Read file paths of changed VTT files in docs_mr/:
echo "Checking for changed VTT files with SHA..."
files=$(git diff --name-only "${GITHUB_SHA}^" "${GITHUB_SHA}" | grep 'docs_mr/.*\.vtt' | tr '\n' ':')
echo "Changed VTT files: $files"

# Convert the colon-separated string to an array
IFS=":" read -ra file_array <<< "$files"

 # Change directory to the app directory for executing main in minervasmemo.py
cd /usr/src/app
ls -l # sanity check for modules

#chmod +x minervasmemo.py

# Iterate over each changed VTT file, sanitize the file name, and process with minervasmemo.py
for file in "${file_array[@]}"; do
    # Sanitize the file name
    sanitized_file=$(echo "$file" | sed 's/docs_mr\///' | sed 's/\.vtt//' | sed 's/[^a-zA-Z0-9]/-/g')
    
    echo "Processing $sanitized_file"
    # Ensure to quote the path to handle spaces
    python minervasmemo.py -i "/github/workspace/docs_mr/$sanitized_file.vtt" --mode summarize >> minervasmemo.log 2>&1
done

cat minervasmemo.log # Print the log file of minervasmemo.py for debugging

# Move the cleaned up transcript and summary to docs_mr/ in the GitHub workspace
mv *summary*.md /github/workspace/docs_mr/ 
mv *token_info.txt /github/workspace/

# Change directory to the GitHub workspace
cd $GITHUB_WORKSPACE || exit

# sanity checks
pwd
echo "Current directory: $(pwd)" 
ls -alh

# Fetch the latest main branch into a temporary branch
git fetch origin main:temp-main

# Checkout the temporary main branch
git checkout temp-main

# Create and checkout a new branch for the Pull Request named after the first file
FEATURE_BRANCH="add-summary-${sanitized_files[0]}"
git checkout -b "$FEATURE_BRANCH"

# Read token and cost information
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
