# Purpose: To summarize the meeting transcript
# Setup
import os
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.llm import LLMChain
from langchain.chains import SimpleSequentialChain
from prompts import init_proompt, refine_prompt, bullet_prompt

load_dotenv()

llm = AzureChatOpenAI(request_timeout=30,
                       model = "summarizer", 
                       temperature=0.5, 
                       deployment_name=os.getenv("OPENAI_MODEL_NAME"),
                       openai_api_key=os.getenv("OPENAI_API_KEY"))

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
    final_summary = overall_simple_chain({"input": docs}, return_only_outputs=True)
    return final_summary['output']