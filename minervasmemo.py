#minervasmemo.py
import argparse
from converter import vtt_to_md
from summarizer_map import generate_summary_map
from splitter import split_transcript 
from tokenizer import count_transcript_tokens
import os

from summarizer_refine import generate_summary_refine

def main():
    parser = argparse.ArgumentParser(description="Convert a .vtt file to a final processed output")
    parser.add_argument("-i", "--input", required=True, help="Path to the .vtt file")

    parser.add_argument("-o", "--output", help="Base path to the output file(s)")
    parser.add_argument("--mode", choices=['convert', 'summarize'], default='convert', help="Operation mode")
    parser.add_argument("--method", choices=['refine', 'map-reduce'], default='map-reduce', help="Method for summarization")


    args = parser.parse_args()

    # Determine the folder based on the input file's location
    # possible_folders = ["", "overview/meetings/webex_mapreduce/", "overview/meetings/webex_refine/"] # uncomment for local testing

    possible_folders = [os.getenv('GITHUB_WORKSPACE'), 
                        os.path.join(os.getenv('GITHUB_WORKSPACE'), 'overview/meetings/webex_mapreduce/'), 
                        os.path.join(os.getenv('GITHUB_WORKSPACE'), 'overview/meetings/webex_refine/')] #for github actions

    folder = None
    for pf in possible_folders:
        file_path = os.path.join(pf, args.input) if not os.path.isabs(args.input) else args.input
        if os.path.exists(file_path):
            folder = pf
            break

    if folder is None:
        print("File not found in any of the specified directories.")
        return

    # Set default output names based on the input file name
    default_output_base = args.input.replace(".vtt", "")
    output_base = args.output if args.output else default_output_base

    if args.mode == 'convert':
        # Convert the .vtt file to a .md file
        convert_output = f"{output_base}_transcript.md"
        vtt_to_md(args.input, convert_output, folder)

    elif args.mode == 'summarize':
        convert_output = f"{output_base}_transcript.md"
        raw_md = vtt_to_md(transcript=args.input, output_path=convert_output, folder=folder)
        docs = split_transcript(raw_md)
        token_count_transcript = count_transcript_tokens(raw_md)
        
        if args.method == 'map-reduce':
            final_summary, aggregated_token_info = generate_summary_map(docs, token_count_transcript)
        
            summary_output = f"{output_base}_summary.md"
            with open(summary_output, 'w') as file:
                file.write(final_summary)

            token_info_output = f"{output_base}_token_info.txt"
            with open(token_info_output, 'w') as file:
                for section, token_info in {f"Total Token Usage: {summary_output}:": aggregated_token_info}.items():
                    file.write(f"--- {section} ---\n")
                    for key, value in token_info.items():
                        file.write(f"{key}: {value}\n")

        elif args.method == 'refine':
            summary_md, token_info = generate_summary_refine(docs)

            summary_output = f"{output_base}_summary.md"
            with open(summary_output, 'w') as file:
                file.write(summary_md)

            token_info_output = f"{output_base}_token_info.txt"
            with open(token_info_output, 'w') as file:
                for key, value in token_info.items():
                    file.write(f"{key}: {value}\n")

if __name__ == "__main__":
    main()