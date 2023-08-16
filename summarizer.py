# Purpose: To summarize the meeting transcript
# Setup
import os
from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import AzureChatOpenAI
from langchain.document_loaders import UnstructuredMarkdownLoader
from converter import vtt_to_md

from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
import openai
from langchain.chains import SimpleSequentialChain
from langchain.prompts import ChatPromptTemplate

openai.api_key = os.environ['OPENAI_API_KEY']

md_path = vtt_to_md("docs/Formal Methods Standup-20230802 0800-1.vtt")

# Recursive splitting to consider different separators in generic text
r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=200, 
    separators=["\n\n", "\n", " ", ""],
    length_function = len
)

########################### Splitting  #################################

def load_transcript(md_path):
    loader = UnstructuredMarkdownLoader(md_path)
    data = loader.load()
    return data

data = load_transcript(md_path)

docs = r_splitter.split_documents(data)

########################### Model ##################################

llm = AzureChatOpenAI(request_timeout=30,
                       model = "summarizer", 
                       temperature=0.5, 
                       deployment_name=os.getenv("OPENAI_MODEL_NAME"),
                       openai_api_key=os.getenv("OPENAI_API_KEY"))

############################ Refine Chain ###########################

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

intermediate_summary = refine_chain({"input_documents": docs}, return_only_outputs=True)

prompt_bullet = ChatPromptTemplate.from_template(
    "You are an excellent executive assistant.\
    Your task is to create a detailed bulleted summary of the following meeting notes lossing as little meaning as possible.\
    Please format your response as markdown code. Highlight datees and agreed upon actions. \
    Summary: {summary}\
    Format: \
    '## Meeting Summary \
    ### Participants\
    ### Discussed\
    - **<Participant 1>:** <participants Message>\
        - point 1\
        - point 2\
        - ...\
    - **<Participant 2>:** <participants Message>\
        - point 1\
        - point 2\
        - ...\
    ### Action Items\
    - <a-list-of-follow-up-actions-with-owner-names>\
    ### Side Comments <if any were made>'"
)

chain_bullet = LLMChain(llm=llm, prompt=prompt_bullet, 
                     output_key="bullet-summary"
                    )

overall_simple_chain = SimpleSequentialChain(chains=[refine_chain, chain_bullet],
                                             verbose=True
                                            )

final_summary = overall_simple_chain({"input": docs}, return_only_outputs=True)

final_summary_output = final_summary['output']

with open(f"{md_path[:-3]}_summary.md", 'w') as file:
    file.write(final_summary_output)


