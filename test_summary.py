from langchain.chat_models import ChatOpenAI
from langchain.chains.mapreduce import MapReduceChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredMarkdownLoader

import tiktoken
encoding_gpt4 = tiktoken.encoding_for_model("gpt-4")
encoding_gpt3 = tiktoken.encoding_for_model("gpt-3.5-turbo")

def vtt_to_md(transcript, output_path):
    """
    Convert a webttv meeting transcript .vtt file to a .md file and remove redundant information

    Parameters:
    - transcript (str): Path to the .vtt file in the docs folder

    Returns:
    - raw_md (str): Path to the raw .md file of the meeting transcript
    """
    if not transcript.startswith("docs/"):
        transcript = f"docs/{transcript}"
    
    vtt_path = transcript
    
    print(f"Reading from {vtt_path}")  # Debugging line
    
    with open(vtt_path, "r", encoding="utf-8") as file:
        vtt_content = file.readlines()

    # Process and refine the content, omitting the "WEBVTT" redundant speaker information
    docs_md = []
    current_speaker = None
    current_start_timestamp = None
    current_end_timestamp = None
    speaker_dialogues = []

    for line in vtt_content:
        line = line.strip()
        print(f"Processing line: {line}")
        # Skip "WEBVTT" and empty lines
        if not line or line == "WEBVTT":
            continue

        # If line contains a speaker's name
        if '"' in line and '-->' not in line:
            new_speaker = line.split('"')[1] # Get the speaker's name
            
            # If we have a previous speaker's dialogues, append them to the output
            if current_speaker and new_speaker != current_speaker:
                docs_md.append("\n")
                # Add the previous speaker's name and timestamps to the output
                docs_md.append(f'### "{current_speaker}" [{current_start_timestamp}-{current_end_timestamp}]')
                docs_md.extend(speaker_dialogues) # Add the speaker's dialogues to the output
                speaker_dialogues = [] # Reset the speaker's dialogues
            current_speaker = new_speaker # Update the current speaker
            current_start_timestamp = None # Reset the start timestamp

        # If line contains a timestamped dialogue
        elif '-->' in line:
            timestamp_start, timestamp_end = line.split(' --> ') # Get the start and end timestamps
            
            # Setting the start timestamp if it's the first dialogue of the current speaker
            if not current_start_timestamp:
                current_start_timestamp = timestamp_start # Setting the start timestamp
            
            # Updating the end timestamp for every dialogue of the current speaker
            current_end_timestamp = timestamp_end

        # If it's a dialogue
        else:
            speaker_dialogues.append(line) # Add the dialogue to the speaker's dialogues

    # Add the last speaker's dialogues to the output
    if current_speaker:
        docs_md.append("\n")
        docs_md.append(f'### "{current_speaker}" [{current_start_timestamp}-{current_end_timestamp}]')
        docs_md.extend(speaker_dialogues)

    # Write to a .md file
    raw_md = vtt_path.replace(".vtt", ".md")

    print(f"Writing to {raw_md}")  # Debugging line
    with open(output_path, "w", encoding="utf-8") as file:

        file.write("\n".join(docs_md))
    print(f"Successfully converted {vtt_path} to {output_path}")
    return output_path


raw_md = vtt_to_md("FormalMethodsStandup-202309200801-1.vtt")


# Recursive splitting to consider different separators in generic text
r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=200, 
    separators=["\n\n", "\n", " ", ""],
    length_function = len
)

def load_transcript(raw_md):
    loader = UnstructuredMarkdownLoader(raw_md)
    data = loader.load()
    return data


# Coun tokens of raw transcript
with open('FormalMethodsStandup-202309200801-1.md', 'r', encoding='utf-8') as file:
    raw_transcript = file.read()

token_count_raw = len(encoding_gpt3.encode(raw_transcript))

def split_transcript(raw_md):
    data = load_transcript(raw_md)
    docs = r_splitter.split_documents(data)
    return docs


docs = split_transcript(raw_md)



# load environment variables
from dotenv import load_dotenv
_ = load_dotenv()

llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")

# Map
map_template = """The following is one of a set of excerpts from an machine-generated transcript of a hybrid team meeting likely containing some transcription errors and might lack coherence in parts. \n
Excerpts:`{text}`\n
Based on this list of excerpts, 
condense the transcript but only WITHOUT loosing ANY information allowing for information-loss-free reconstruction of the original transcript. \n
correct obvious transcription errors that do not match the context. \n
Note that longer segments attributed to one speaker might correspond to multiple speakers attending the hybrid meeting in person recorded as one speaker. \n
Only include speaker attribution if it is directly relevant to the discussed content otherwise refer to a speaker as "the team". Focus on information-loss-free content condensation. \n
Thus provide a detailed and cohesive meeting transcript by correcting any transcription errors. Work step by step. \n
Comprehensive Meeting Notes:"""
# map_prompt = PromptTemplate.from_template(map_template)
# map_chain = LLMChain(llm=llm, prompt=map_prompt)
map_prompt_template = PromptTemplate (
    input_variables=["text"],
    template=map_template
)

# Reduce
reduce_template = """You are an excellent executive assistant. The following is one of a set of excerpts from a meeting transcripts of a recent hybrid meeting: \n
Excerpt:`{text}`\n
Take these and in a stepwise manner condense the transcript text in one coherent document but WITHOUT loosing ANY meaning allowing for information-loss-free reconstruction of the original transcript. \n
Note that longer segments attributed to one speaker might correspond to multiple speakers attending the hybrid meeting in person recorded as one speaker. \n
To accomadte this ONLY include speaker attribution if it is DIRECTLY relevant to the discussed content otherwise refer to a speaker as "the team".\n
Focus on discussed topics and NOT participant attribution of talking points and action items unless explicitly mentioned by a speaker. \n
Thus step by step distill a condensed but information rich, complete and cohesive summary for optimal information retrieval. \n
Meeting Summary:"""
# reduce_prompt = PromptTemplate.from_template(reduce_template)
combine_prompt_template = PromptTemplate(
    input_variables=["text"],
    template=reduce_template
)

from langchain.chains.summarize import load_summarize_chain

summary_chain1 = load_summarize_chain (
    llm=llm,
    chain_type='map_reduce',
    map_prompt=map_prompt_template,
    combine_prompt=combine_prompt_template,
    verbose=False,
    token_max=4000
)
first_summary=summary_chain1.run(docs)

# Count tokens of first summary
token_count_first_summary = len(encoding_gpt4.encode(first_summary))
token_count_first_summary

# If token_count_first_summary > 4000 enter a second map reduce chain:
# split the first summary using recursive splitter
first_summary_docs = r_splitter.create_documents([first_summary])

# Second Map Reduce Chain:
# Map2
map_template2 = """The following is a set of excerpts from an meeting summary of a hybrid team meeting. \n
Excerpt:`{text}`\n
Based on this list of excerpts, 
condense the transcript but only WITHOUT loosing ANY information allowing for information-loss-free reconstruction of the original transcript. \n
correct obvious transcription errors that do not match the context. \n
Only include speaker attribution if it is directly relevant to the discussed content otherwise refer to a speaker as "the team". Focus on information-loss-free content condensation. \n
Thus provide a detailed and cohesive meeting summary. Work step by step. \n
Comprehensive Meeting Notes:"""

map_prompt_template2 = PromptTemplate (
    input_variables=["text"],
    template=map_template2
)

# Reduce2
reduce_template2 = """You are an excellent executive assistant. The following is set of excerpts from a meeting transcripts of a recent hybrid meeting: \n
Excerpt:`{text}`\n
Take these and in a stepwise manner condense the transcript text in one coherent document but WITHOUT loosing ANY meaning allowing for information-loss-free reconstruction of the original transcript. \n
Note that longer segments attributed to one speaker might correspond to multiple speakers attending the hybrid meeting in person recorded as one speaker. \n
To accomadte this ONLY include speaker attribution if it is DIRECTLY relevant to the discussed content otherwise refer to a speaker as "the team".\n
Focus on discussed topics and NOT participant attribution of talking points and action items unless explicitly mentioned by a speaker. \n
Thus step by step distill a condensed but information rich, complete and cohesive summary for optimal information retrieval. \n
Meeting Summary:"""
combine_prompt_template2 = PromptTemplate(
    input_variables=["text"],
    template=reduce_template2
)

# Run Second Map Reduce Chain:
summary_chain2 = load_summarize_chain (
    llm=llm,
    chain_type='map_reduce',
    map_prompt=map_prompt_template2,
    combine_prompt=combine_prompt_template2,
    verbose=False,
    token_max=4000
)
second_summary=summary_chain1.run(first_summary_docs)


# Bullet Prompt, continues here either after first or second map reduce chain:
from langchain.prompts import ChatPromptTemplate

# Set final summary depending on whether first or second map reduce chain was run:

if token_count_first_summary > 4000:
    summary = second_summary
else:
    summary = first_summary

# Create variable to optionally set the model type to GPT-4 or gpt-3.5-turbo:
# ...

# Define default values for variables that can be respecified on demand in the final function call 
team_name = "Formal Methods Group of the Max Planck Institute for Human Development Berlin (MPIB)"
team_members = "Aaron Peikert, Andreas Brandmaier, Hannes Diemerling, Leonie Hagitte, Maximilian Ernst, Moritz Ketzer, Nicklas Hafiz, Ulman Lindenberger, Valentin Kriegmair"


bullet_prompt = ChatPromptTemplate.from_template(
    """You are an excellent executive assistant.\n
    The following are meeting notes from a recent team meeting of the {team_name}:\n
    Summary: {summary}\n
    Your task is to create a well structured bulleted document of these meeting notes in Markdown format loosing as little meaning as possible.\n
    Instructions:\n
    - Focus on discussed topics and NOT participant attribution of talking points and action items UNLESS explicitly mentioned by a speaker. \n
    - Highlight dates and agreed upon action items. Work step by step, format your response in Markdown according to the following sample strucutre:\n
    - Correct potentially mispelled names of participants according to the following list of regular team members:\n
    - {team_members}\n
    Sample Format: \n
    Markdown:```## Meeting Summary \n
    ### Participants\n
    - <list of participants in the meeting you can identify>\n
    ### Discussed\n
    - **<First Discussion Point>:**\n
        - <sub-point 1>\n
        - <sub-point 2>\n
        - ...\
    - **<Second Discussion Point>:**\n
        - <sub-point 1>\n
        - <sub-point 2>\n
        - ...\n
    ...
    ### Action Items\n
    - <a list of follow up actions. Include owner names ONLY if applicable>\n
    ### Side Comments <trivial side comments if any were made, otherwise ommit>```"""
)


bullet_chain = LLMChain(llm=llm, prompt=bullet_prompt,
                        output_key="bullet-summary")

# Run Bullet Chain:
bullet_chain.run(summary = summary, team_name = team_name, team_members = team_members)