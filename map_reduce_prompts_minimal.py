from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate

# Map
map_template = """You are an excellent executive assistant. You get an automated meeting transcript with transcription error due to autmoatic voice recognition, please ignore those. \n
Your task is to compress them as much as possible without loosing too much meaning. \n
Excerpts:`{text}`\n
Comprehensive Meeting Notes:"""
# map_prompt = PromptTemplate.from_template(map_template)
# map_chain = LLMChain(llm=llm, prompt=map_prompt)
map_prompt_template = PromptTemplate (
    input_variables=["text"],
    template=map_template
)

# Reduce
reduce_template = """You are an excellent executive assistant. The following is one of a set of excerpts from a meeting transcripts of a recent hybrid meeting: \n
Excerpt:`{text}`\n
Take these and in a stepwise manner condense the transcript text in one coherent document but WITHOUT loosing ANY meaning allowing for information-loss-free reconstruction of the original transcript. \n
Thus step by step distill a condensed but information rich, complete and cohesive summary for optimal information retrieval. \n
Meeting Summary:"""
# reduce_prompt = PromptTemplate.from_template(reduce_template)
combine_prompt_template = PromptTemplate(
    input_variables=["text"],
    template=reduce_template
)


# Second Map Reduce Chain:
# Map2
map_template2 = """You are an excellent executive assistant. You get an automated meeting transcript with transcription error due to autmoatic voice recognition, please ignore those. \n
Your task is to compress them as much as possible without loosing too much meaning. \n
Excerpts:`{text}`\n
Comprehensive Meeting Notes:"""

map_prompt_template2 = PromptTemplate (
    input_variables=["text"],
    template=map_template2
)

# Reduce2
reduce_template2 = """You are an excellent executive assistant. The following is one of a set of excerpts from a meeting transcripts of a recent hybrid meeting: \n
Excerpt:`{text}`\n
Take these and in a stepwise manner condense the transcript text in one coherent document but WITHOUT loosing ANY meaning allowing for information-loss-free reconstruction of the original transcript. \n
Thus step by step distill a condensed but information rich, complete and cohesive summary for optimal information retrieval. \n
Meeting Summary:"""
combine_prompt_template2 = PromptTemplate(
    input_variables=["text"],
    template=reduce_template2
)

bullet_prompt = ChatPromptTemplate.from_template(
    "You are an excellent executive assistant.\
    Your task is to create a detailed bulleted summary of the following meeting notes lossing as little meaning as possible.\
    Please format your response as markdown code. Highlight dates and agreed upon actions. \
    Summary: {summary}\
    Format: \
    '## Meeting Summary \
    ### Participants\
    ### Discussed\
    - **<Agenda Item 1>:**\
        - point 1\
        - point 2\
        - ...\
    - **<Agenda Item 2>:**\
        - point 1\
        - point 2\
        - ...\
    ### Action Items\
    - <a-list-of-follow-up-actions-with-owner-names>\
    ### Side Comments <if any were made>'"
)

# a new prompt template for a gpt4 prompt that taks a whole transcript as one as input
# and outputs a summary of the transcript
all_in_one_prompt_template = ChatPromptTemplate.from_template(
    """You are an excellent executive assistant.\n
    You are given an automated meeting transcript with transcription error due to autmoatic voice recognition, please ignore those.\n
    Your task is to compress them as much as possible without loosing too much meaning.\n
    Transcript: {docs}\n
    Format your output in Markdown in the following way:
    '## Meeting Summary \
    ### Participants\
    ### Discussed\
    - **<Agenda Item 1>:**\
        - point 1\
        - point 2\
        - ...\
    - **<Agenda Item 2>:**\
        - point 1\
        - point 2\
        - ...\
    ### Action Items\
    - <a-list-of-follow-up-actions-with-owner-names>\
    ### Side Comments <if any were made>'\n""")