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

md_path = vtt_to_md("docs/Formal Methods Standup-20230802 0800-1.vtt")

# Recursive splitting to consider different separators in generic text
r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=200, 
    separators=["\n\n", "\n", " ", ""],
    length_function = len
)

######################## Option 1 Context Aware Split by Speaker ################################

with open(md_path, 'r', encoding='utf-8') as file:
    md_script = file.read()

headers_to_split_on = [("###", "Speaker 3")]

md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

speaker_splits = md_splitter.split_text(md_script)

speaker_recursive_splits = r_splitter.split_documents(speaker_splits)


########################### Option 2 Blind Splitting #################################

def load_transcript(md_path):
    loader = UnstructuredMarkdownLoader(md_path)
    data = loader.load()
    return data

data = load_transcript(md_path)

txt = ' '.join([d.page_content for d in data])

blind_recursive_splits = r_splitter.split_documents(txt)

################################################################################

model = AzureChatOpenAI(request_timeout=30,
                                    model = "summarizer", 
                                    temperature=0.1, 
                                    deployment_name=os.getenv("OPENAI_MODEL_NAME"))



