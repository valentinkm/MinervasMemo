#TEST
# Purpose: To summarize the meeting transcript
# Libraries
import os
from dotenv import load_dotenv
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.llm import LLMChain
from langfuse.callback import CallbackHandler
from langchain.callbacks import get_openai_callback
from langchain.chains.llm import LLMChain
from langchain.chat_models import ChatOpenAI
from map_reduce_prompts_minimal import zero_shot_prompt

    llm_zero_shot = ChatOpenAI(temperature=0.7, model_name="gpt-4")


