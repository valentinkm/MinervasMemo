from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate

# Map
map_template = """The following is a set of documents
{docs}
Based on this list of docs, please identify the main themes 
Helpful Answer:"""
map_prompt = PromptTemplate.from_template(map_template, input_variables=["docs"])

# Reduce
reduce_template = """The following is set of summaries:
{doc_summaries}
Take these and distill it into a final, consolidated summary of the main themes. 
Helpful Answer:"""
reduce_prompt = PromptTemplate.from_template(reduce_template)

bullet_prompt = ChatPromptTemplate.from_template(
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