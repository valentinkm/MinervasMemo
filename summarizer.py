# Purpose: To summarize the meeting transcript
# Setup
import os
from dotenv import load_dotenv
load_dotenv()
from langchain.chat_models import AzureChatOpenAI

# Model
model = AzureChatOpenAI(request_timeout=30,
                        model = "summarizer", 
                        temperature=0.1, 
                        deployment_name=os.getenv("OPENAI_MODEL_NAME"))





                

