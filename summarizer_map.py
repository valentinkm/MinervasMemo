# Purpose: To summarize the meeting transcript
# Setup
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.llm import LLMChain
from langchain.chains import SimpleSequentialChain
from langfuse.callback import CallbackHandler
from langchain.callbacks import get_openai_callback


# Setup map reduce
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

from prompts import map_prompt, reduce_prompt, bullet_prompt


# Initialization variables set to None
llm = None
map_reduce_chain = None
bullet_chain = None
overall_simple_chain = None
handler = None

def initialize_summarizer():
    global llm, map_reduce_chain, bullet_chain, overall_simple_chain, handler
    
    load_dotenv()
    
    PUBLIC_KEY = os.getenv('PUBLIC_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    handler = CallbackHandler(PUBLIC_KEY, SECRET_KEY)
    
    llm = ChatOpenAI(temperature=0.5, model_name="gpt-3.5-turbo")

    
    map_reduce_chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        return_intermediate_steps=False,
        map_prompt=map_prompt,
        refine_prompt=reduce_prompt
    )
    
    bullet_chain = LLMChain(llm=llm, prompt=bullet_prompt, output_key="bullet-summary")
    
    overall_simple_chain = SimpleSequentialChain(chains=[map_reduce_chain, bullet_chain], verbose=True)
    

def generate_summary(docs):
    global llm, map_reduce_chain, bullet_chain, overall_simple_chain, handler
    
    if llm is None:
        initialize_summarizer()
    
    token_info = {}

    with get_openai_callback() as cb:
        final_summary = overall_simple_chain({"input": docs}, return_only_outputs=True, callbacks=[handler])
        
        token_info['Total Tokens'] = cb.total_tokens
        token_info['Prompt Tokens'] = cb.prompt_tokens
        token_info['Completion Tokens'] = cb.completion_tokens
        token_info['Total Cost (USD)'] = cb.total_cost
        
    return final_summary['output'], token_info