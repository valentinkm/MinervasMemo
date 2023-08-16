# Purpose: To summarize the meeting transcript
# Setup
import os
from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import AzureChatOpenAI
from langchain.document_loaders import UnstructuredMarkdownLoader
from converter import vtt_to_md

from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.mapreduce import MapReduceChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
import openai
from langchain.chains.mapreduce import MapReduceChain
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.chat_models import ChatOpenAI

openai.api_key = os.environ['OPENAI_API_KEY']

md_path = vtt_to_md("docs/Formal Methods Standup-20230802 0800-1.vtt")

# Recursive splitting to consider different separators in generic text
r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=200, 
    separators=["\n\n", "\n", " ", ""],
    length_function = len
)

######################## Splitting Option 1 Context Aware Split by Speaker ######################

with open(md_path, 'r', encoding='utf-8') as file:
    md_script = file.read()

headers_to_split_on = [("###", "Speaker 3")]

md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

speaker_splits = md_splitter.split_text(md_script)

speaker_recursive_splits = r_splitter.split_documents(speaker_splits)


########################### Splitting Option 2 Blind Splitting #################################

def load_transcript(md_path):
    loader = UnstructuredMarkdownLoader(md_path)
    data = loader.load()
    return data

data = load_transcript(md_path)

blind_recursive_splits = r_splitter.split_documents(data)

############################ Summarize Option 1 Map Reduce #################################################
docs = blind_recursive_splits

llm = AzureChatOpenAI(request_timeout=30,
                       model = "summarizer", 
                       temperature=0.5, 
                       deployment_name=os.getenv("OPENAI_MODEL_NAME"),
                       openai_api_key=os.getenv("OPENAI_API_KEY"))


# Map
map_template = """Act as an excellent executive assistant. The following is a set of machine generated speaker transcripts of a meeting sometimes containing words that do not fit the context and may need to be replaced to make sense.
{docs}
Based on this list of meeting excerpts, please identify all relevant talking points and agreed upon action items. Regular participants of the meeting include: Aaron Peikert, Timo von Oertzen, Hannes Diemerling, Leonie Hagitte, Maximilian Ernst, Valentin Kriegmair, Leo Kosanke, Ulman Lindenberger, Moritz Ketzer and Nicklas Hafiz.
CONCISE SUMMARY IN ENGLISH:"""
map_prompt = PromptTemplate.from_template(map_template)
map_chain = LLMChain(llm=llm, prompt=map_prompt)

# Reduce
reduce_template = """Act as an excellent executive assistant. The following is set of summaries of a team meeting
{doc_summaries}
Take these and distill it into a detailed final, consolidated summary of the main talking points and action items of the whole meeting.
Helpful Answer:"""
reduce_prompt = PromptTemplate.from_template(reduce_template)
reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

# Takes a list of documents, combines them into a single string, and passes this to an LLMChain
combine_documents_chain = StuffDocumentsChain(
    llm_chain=reduce_chain, document_variable_name="doc_summaries"
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

# result = map_reduce_chain.run(docs)

############################ Summarize Option 2 Refine #################################################

from langchain.prompts import PromptTemplate

prompt_template = """You are an excellent executive assistent. You are given an excerpt of a machine generated transcript of a stand-up meeting of the formal methods group at MPI-Berlin. The script sometimes contains words that do not fit the context or misspelled names and may need to be replaced accordingly to make sense.
    {text}
    Based on the excerpt please identify all relevant talking points and agreed upon action items. Do NOT make any points up. For context: Team members regulalry attending the meeting include: Aaron Peikert, Timo von Oertzen, Hannes Diemerling, Leonie Hagitte, Maximilian Ernst, Valentin Kriegmair, Leo Kosanke, Ulman Lindenberger, Moritz Ketzer and Nicklas Hafiz.
    Tone: formal
    Format: 
    - Concise and detailed meeting summary
    - Participants: <participants>
    - Discussed: <Discussed-items>
    - Follow-up actions: <a-list-of-follow-up-actions-with-owner-names>
    Tasks:
    - Highlight who is speaking, action items, dates and agreements
    - Step by step list all points of each speaker or group of speakers
    - Work step by step.
    CONCISE SUMMARY IN ENGLISH:"""

PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

refine_template = (
        "Your are an excellent executive assistent \n"
        "Your job is to produce a final summary\n"
        "We have provided an existing meeting summary up to a certain point: {existing_answer}\n"
        "We have the opportunity to refine the existing summary"
        "(only if needed) with some more context below.\n"
        "------------\n"
        "{text}\n"
        "------------\n"
        f"Given the new context, refine the original summary: following the format"
        "Participants: <Participants>"
        "Discussed: <Discussed-items>"
        "Follow-up actions: <a-list-of-follow-up-actions-with-owner-names>"
        "Highlight who is speaking, action items, dates and agreements"
        "List points for each section by a speaker or the group in detail."
        "Work step by step."
        "If the context isn't useful, return the original summary, do NOT make anything up. Highlight agreements and follow-up actions and owners."
)

refine_prompt = PromptTemplate(
        input_variables=["existing_answer", "text"],
        template=refine_template,
)

refine_chain = load_summarize_chain(
        llm,
        chain_type="refine",
        return_intermediate_steps=False,
        question_prompt=PROMPT,
        refine_prompt=refine_prompt,
)

# refine_result = refine_chain({"input_documents": docs}, return_only_outputs=True)

from langchain.chains import SimpleSequentialChain
from langchain.prompts import ChatPromptTemplate


prompt_bullet = ChatPromptTemplate.from_template(
    "You are an excellent executive assistant.\
    Your task is to create a detailed bulleted summary of the following meeting notes.\
    Please format your response as markdown code. Highlight agreed upon actions \
    Summary: {summary}\
    Format: \
    '## Meeting Summary \
    ### Participants\
    ### Discussed\
    - **Speaker 1**\
        - points \
        - ...\
    - ...\
    ### Action Items\
    - <a-list-of-follow-up-actions-with-owner-names>\
    ### Side Comments'"
)

chain_bullet = LLMChain(llm=llm, prompt=prompt_bullet, 
                     output_key="bullet-summary"
                    )

overall_simple_chain = SimpleSequentialChain(chains=[refine_chain, chain_bullet],
                                             verbose=True
                                            )

overall_simple_chain({"input": docs}, return_only_outputs=False)