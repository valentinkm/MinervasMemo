from langchain.chat_models import ChatOpenAI
from langchain.chains.mapreduce import MapReduceChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredMarkdownLoader

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



raw_md = vtt_to_md("FormalMethodsStandup-202309200801-1.vtt", "FormalMethodsStandup-202309200801-1.md")



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

def split_transcript(raw_md):
    data = load_transcript(raw_md)
    docs = r_splitter.split_documents(data)
    return docs

docs = load_transcript(raw_md)

docs = split_transcript(raw_md)


# load environment variables
from dotenv import load_dotenv
_ = load_dotenv()

llm = ChatOpenAI(temperature=0.5, model_name="gpt-3.5-turbo")

# Map
map_template = """The following is a set of excerpts from an machine-generated transcript of a hybrid team meeting likely containing some transcription errors and might lack coherence in parts. \n
{docs}
Based on this list of excerpts, 
condense the transcript but only WITHOUT loosing ANY information allowing for information-loss-free reconstruction of the original transcript. \n
correct obvious transcription errors that do not match the context. \n
Note that longer segments attributed to one speaker might correspond to multiple speakers attending the hybrid meeting in person recorded as one speaker. \n
Only include speaker attribution if it is directly relevant to the discussed content otherwise refer to a speaker as "the team". Focus on information-loss-free content condensation. \n
Thus provide a detailed and cohesive meeting transcript by correcting any  Dilligently work step by step. \n
Comprehensive Meeting Notes:"""
map_prompt = PromptTemplate.from_template(map_template)
map_chain = LLMChain(llm=llm, prompt=map_prompt)


# Reduce
reduce_template = """You are an excellent executive assistant. The following is set of transcripts of a recent hybrid meeting: \n
{docs}
Take these and in a stepwise manner condense the transcript text but WITHOUT loosing ANY information allowing for information-loss-free reconstruction of the original transcript. \n
Note that longer segments attributed to one speaker might correspond to multiple speakers attending the hybrid meeting in person recorded as one speaker. \n
Only include speaker attribution if it is directly relevant to the discussed content otherwise refer to a speaker as "the team". Focus on information-loss-free content condensation. \n
Thus step by step distill a condensed, cohesive and complete summary for optimal information retrieval. \n
Meeting Summary:"""
reduce_prompt = PromptTemplate.from_template(reduce_template)


"""You are an excellent and highly committed executive assistant. The following is set of comprehensive notes on a recent meeting:
{docs}
Take these and in a stepwise manner identify all relevant talking points and the thematic strucutre of the meeting. Highlight agreed upon action items and decisions made.
In this way provide a well strucutred, consolidated meeting summary that can be used for efficient and comprehensive retrosprective information retrieval.
Well Structured Meeting Summary:"""

# Run chain
reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

# Takes a list of documents, combines them into a single string, and passes this to an LLMChain
combine_documents_chain = StuffDocumentsChain(
    llm_chain=reduce_chain, document_variable_name="docs"
)

# Combines and iteravely reduces the mapped documents
reduce_documents_chain = ReduceDocumentsChain(
    # This is final chain that is called.
    combine_documents_chain=combine_documents_chain,
    # If documents exceed context for `StuffDocumentsChain`
    collapse_documents_chain=combine_documents_chain,
    # The maximum number of tokens to group documents into.
    token_max=4000,
)

# Combining documents by mapping a chain over them, then combining results
map_reduce_chain = MapReduceDocumentsChain(
    # Map chain
    llm_chain=map_chain,
    # Reduce chain
    reduce_documents_chain=reduce_documents_chain,
    # The variable name in the llm_chain to put the documents in
    document_variable_name="docs",
    # Return the results of the map steps in the output
    return_intermediate_steps=False,
)






print(map_reduce_chain.run(docs))

