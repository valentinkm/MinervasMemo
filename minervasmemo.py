import argparse
from converter import vtt_to_md
from summarizer import generate_summary
from splitter import split_transcript

def main():
    parser = argparse.ArgumentParser(description="Convert a .vtt file to a final processed output")
    parser.add_argument("-i", "--input", required=True, help="Path to the .vtt file")

    parser.add_argument("-o", "--output", help="Base path to the output file(s)")
    parser.add_argument("--mode", choices=['convert', 'summarize'], default='convert', help="Operation mode")

    args = parser.parse_args()

    # Set default output names based on the input file name
    default_output_base = args.input.replace(".vtt", "")
    output_base = args.output if args.output else default_output_base

    if args.mode == 'convert':
        # Convert the .vtt file to a .md file
        convert_output = f"{output_base}_transcript.md"
        vtt_to_md(args.input, convert_output)

    elif args.mode == 'summarize':
        # First, convert the .vtt file to a .md file
        convert_output = f"{output_base}_transcript.md"
        raw_md = vtt_to_md(args.input, convert_output)

        # Split .md in chunks
        docs = split_transcript(raw_md)
        
        # Generate llm based summary
        summary_output = f"{output_base}_summary.md"
        summary_md = generate_summary(docs)
        
        with open(summary_output, 'w') as file:

            file.write(summary_md)

if __name__ == "__main__":
    main()