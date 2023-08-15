# Purpose: To summarize the meeting transcript
# Setup
import os
import argparse
from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import AzureChatOpenAI
from langchain.document_loaders import UnstructuredMarkdownLoader
from converter import vtt_to_md

from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter



def summarize_transcript(vtt_file_path):
    md_path = vtt_to_md(vtt_file_path)
    loader = UnstructuredMarkdownLoader(md_path, mode = "elements")
    data = loader.load()
    return data

data = summarize_transcript("docs/Formal Methods Standup-20230802 0800-1.vtt")



docs = [Document(page_content=t) for t in data[:]]


model = AzureChatOpenAI(request_timeout=30,
                                    model = "summarizer", 
                                    temperature=0.1, 
                                    deployment_name=os.getenv("OPENAI_MODEL_NAME"))

