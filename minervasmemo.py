import argparse
from converter import vtt_to_md
from summarizer import summarizer

def main ():
    parser = argparse.ArgumentParser(description="Convert a .vtt file to a final processed output")
    parser.add_argument("-i", "--input", required=True, help="Path to the .vtt file")
    parser.add_argument("-o", "--output", required=True, help="Path to the output file")
                        
    args = parser.parse_args()

    # Convert the .vtt file to a .md file
    raw_md_path = vtt_to_md(args.input)

    # LLM
    md_path = summarizer(raw_md_path)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(md_path)

if __name__ == "__main__":
    main()

    
