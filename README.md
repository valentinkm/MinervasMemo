# MinervasMemo
A LLM based summarization tool of webex meeting transcripts using Openai's ChatGPT 3.5 and langchain.

## Installation
Install dependencies and activate the conda environment for MinervasMemo with  

`conda env create -f environment.yml`

## Usage
### Local Usage
- Deposit your transcript VTT files in the "docs/" subdirectory.
- To convert and summarize a VTT transcript file run:
  
`python minervasmemo.py -i "sample.vtt" --mode summarize`
- To just convert a VTT transcript to a cleaned up transcript in Markdown format run:

`python minervasmemo.py -i "sample.vtt" --mode convert`

### Remote Usage for Collaborators
- Commit and push your VTT webex transcript file (e.g. "FormalMethodsStandup-230913.vtt") into 
    - the "docs_mr/" directory of this repository on the main branch (don't use spaces in the filename) for map-reduce LLM-chain based summarization
    - the "docs_refine/" directory of this repository on the main branch (don't use spaces in the filename) for a refine-chain LLM-chain based summarization
- Review your cleaned up transcript (e.g. "FormalMethodsStandup-230913_transcript.vtt") and summary ("FormalMethodsStandup-230913_summary.vtt") in a new pull request to the main branch.
