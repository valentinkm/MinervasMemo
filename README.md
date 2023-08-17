# MinervasMemo
A langchain script for summarizing transcripts of meetings and extracting action items

# Installation
Install dependencies and activate the conda environment for MinervasMemo with  

`conda env create -f environment.yml`

# Usage
- Deposit your `.vtt` transcript files in `docs` subdirectory.
- To convert and summarize a .vtt transcript file, use the following command:

    `python minervasmemo.py -i "path_to_vtt_file" -o "output_summary_file.md"`

# Licensing
The code in this project is licensed under MIT license.