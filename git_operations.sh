#!/bin/bash
echo "Starting git_operations.sh script"


# Check if mandatory environment variables are set
if [ -z "$OPENAI_API_KEY" ] || [ -z "$GH_TOKEN" ] || [ -z "$PUBLIC_KEY" ] || [ -z "$SECRET_KEY" ]; then
  echo "Required environment variables are missing. Set OPENAI_API_KEY, GH_TOKEN, PUBLIC_KEY, and SECRET_KEY as secrets in your GitHub repository settings."
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
echo "Contents of overview/meetings/webex_mapreduce/ directory:" 
ls -alh overview/meetings/webex_mapreduce/
echo "The current branch is:"
git branch
echo "GITHUB_REF: ${GITHUB_REF}"
echo "GITHUB_SHA: ${GITHUB_SHA}"

# Checking for changed VTT files
echo "Checking for changed VTT files with SHA..."
files=$(git diff --name-only "${GITHUB_SHA}^" "${GITHUB_SHA}" | grep 'overview/meetings/webex_mapreduce/.*\.vtt' | tr '\n' ':')
echo "Changed VTT files: $files"

# Convert the colon-separated string to an array
IFS=":" read -ra file_array <<< "$files"

# Change directory to the app directory for executing main in minervasmemo.py
cd /usr/src/app
ls -l # sanity check for modules

#chmod +x minervasmemo.py

# Iterate over each changed VTT file, sanitize the file name, and process with minervasmemo.py
sanitized_files=()
for file in "${file_array[@]}"; do
    # Extract just the filename without path
    sanitized_file=$(basename "$file" | sed 's/\.vtt$//')

    echo "Processing $sanitized_file"
    # Ensure to use the full path for input, properly quoted to handle spaces
    python minervasmemo.py -i "$file" --mode summarize >> minervasmemo.log 2>&1
done


cat minervasmemo.log # Print the log file of minervasmemo.py for debugging

# Move the cleaned up transcript and summary to overview/meetings/webex_mapreduce/ in the GitHub workspace
# can be removed
# mv *summary*.md /github/workspace/overview/meetings/webex_mapreduce/ 
# mv *token_info.txt /github/workspace/ 

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
token_info=$(cat overview/meetings/summaries/*_token_info.txt | sed ':a;N;$!ba;s/\n/\\n/g')
info="$token_info"
echo "Token and Cost Info:"
echo -e "$info"


# Commit changes and push to the new branch
git add overview/meetings/summaries/*.md
git add overview/meetings/transcripts/*.md
git status
if git commit -m "Add cleaned up transcript and summary as markdown"; then
  git push origin "$FEATURE_BRANCH"
  
  # Create Pull Request with the GitHub CLI
  gh pr create --base main --head "$FEATURE_BRANCH" \
    --title "Add cleaned up transcript and summary" \
    --body "$info" \
    --reviewer "$GITHUB_ACTOR"
else
  echo "No changes to commit"
fi
