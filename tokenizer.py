#tokenizer.py
import tiktoken
import os
encoding_gpt4 = tiktoken.encoding_for_model("gpt-4")
encoding_gpt3 = tiktoken.encoding_for_model("gpt-3.5-turbo")


def count_transcript_tokens(raw_md):
    if not os.path.isfile(raw_md):
        raise FileNotFoundError(f"The markdown file {raw_md} does not exist.")

    with open(raw_md, 'r', encoding='utf-8') as file:
        content = file.read()

    token_count_transcript = len(encoding_gpt4.encode(content))
    return token_count_transcript

