# Purpose: To summarize the meeting transcript
# Setup
import os
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.llm import LLMChain
from langchain.chains import SimpleSequentialChain
from prompts import init_proompt, refine_prompt, bullet_prompt
from langfuse.callback import CallbackHandler

# Initialization variables set to None
llm = None
refine_chain = None
bullet_chain = None
overall_simple_chain = None
handler = None

def initialize_summarizer():
    global llm, refine_chain, bullet_chain, overall_simple_chain, handler
    
    load_dotenv()
    
    PUBLIC_KEY = os.getenv('PUBLIC_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    handler = CallbackHandler(PUBLIC_KEY, SECRET_KEY)
    
    llm = AzureChatOpenAI(request_timeout=30,
                          model="summarizer",
                          temperature=0.5,
                          deployment_name=os.getenv("OPENAI_MODEL_NAME"),
                          openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    refine_chain = load_summarize_chain(
        llm,
        chain_type="refine",
        return_intermediate_steps=False,
        question_prompt=init_proompt,
        refine_prompt=refine_prompt
    )
    
    bullet_chain = LLMChain(llm=llm, prompt=bullet_prompt, output_key="bullet-summary")
    
    overall_simple_chain = SimpleSequentialChain(chains=[refine_chain, bullet_chain], verbose=True)
    

def generate_summary(docs):
    global llm, refine_chain, bullet_chain, overall_simple_chain, handler
    
    if llm is None:
        initialize_summarizer()
        
    final_summary = overall_simple_chain({"input": docs}, return_only_outputs=True, callbacks=[handler])
    return final_summary['output']
