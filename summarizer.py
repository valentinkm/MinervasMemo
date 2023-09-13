# Purpose: To summarize the meeting transcript
# Setup
import os
from dotenv import load_dotenv
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.llm import LLMChain
from langchain.chains import SimpleSequentialChain
from prompts import init_proompt, refine_prompt, bullet_prompt
from langchain.chat_models import ChatOpenAI
from langfuse.callback import CallbackHandler

load_dotenv()

PUBLIC_KEY = os.getenv('PUBLIC_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

handler = CallbackHandler(PUBLIC_KEY, SECRET_KEY)

llm = ChatOpenAI(temperature=0.5, model_name="gpt-3.5-turbo")


refine_chain = load_summarize_chain(
        llm,
        chain_type="refine",
        return_intermediate_steps=False,
        question_prompt=init_proompt,
        refine_prompt=refine_prompt,
)

# intermediate_summary = refine_chain({"input_documents": docs}, return_only_outputs=True)

bullet_chain = LLMChain(llm=llm, prompt=bullet_prompt, 
                     output_key="bullet-summary"
                    )

overall_simple_chain = SimpleSequentialChain(chains=[refine_chain, bullet_chain],
                                             verbose=True
                                            )

def generate_summary(docs):
    final_summary = overall_simple_chain({"input": docs}, return_only_outputs=True, callbacks=[handler])
    return final_summary['output']