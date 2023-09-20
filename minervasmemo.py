import argparse
from converter import vtt_to_md
from summarizer import generate_summary
from splitter import split_transcript

def main ():
    parser = argparse.ArgumentParser(description="Convert a .vtt file to a final processed output")
    parser.add_argument("-i", "--input", required=True, help="Path to the .vtt file")
    parser.add_argument("-o", "--output", required=True, help="Path to the output file")
    parser.add_argument("--mode", choices=['convert', 'summarize', 'all'], default='all', help="Operation mode")

    args = parser.parse_args()

    if args.mode in ['convert', 'all']:
        # Convert the .vtt file to a .md file
        raw_md = vtt_to_md(args.input)
    
    if args.mode in ['summarize', 'all']:
        # Convert the .vtt file to a .md file
        raw_md = vtt_to_md(args.input)
        # Split .md in chunks
        docs = split_transcript(raw_md)
        # Generate llm based summary
        summary_md = generate_summary(docs)
        with open(args.output, 'w') as file:
            file.write(summary_md)

if __name__ == "__main__":
    main()

    
