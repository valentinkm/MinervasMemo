from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate

# Map
map_template = """You are an excellent executive assistant. You get an automated meeting transcript with transcription error due to autmoatic voice recognition, please ignore those. \n
Your task is to summarize the transcript by condensing it without loosing meaning.\n
Excerpts:`{text}`\n
Comprehensive Meeting Notes:"""
# map_prompt = PromptTemplate.from_template(map_template)
# map_chain = LLMChain(llm=llm, prompt=map_prompt)
map_prompt_template = PromptTemplate (
    input_variables=["text"],
    template=map_template
)

# Reduce
reduce_template = """You are an excellent executive assistant. The following is a set of excerpts from meeting transcripts of a recent hybrid meeting: \n
Excerpt:`{text}`\n
Your task is to combine these into one coherent and concise document but WITHOUT loosing meaning. \n
Step by step distill the text into a comprehensive and cohesive summary of the meeting. \n
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
    """
    You are an excellent executive assistance. You are given a summary of a hybrid video conference:\n
    Use this to create a well structured concise summary from this in Markdown format.\n
    Key Aspects to focus on in your summary are:\n
    - Clarity and Accuracy: Ensure the summary is clear and accurate, accounting for potential transcription errors.\n
    - Highlight Key Points by emphasizing agreed upon decisions, action items, and dates.\n
    - Organize Efficiently: Use structured sections in the summary.\n
    - Include one section called "Action Items" containing all agreed upon decisions and action items with dates and responsible persons if applicable.\n
    - Keep the summary concise and to the point for efficient future reference of key elements.\n
    - Format: Use Markdown formatting for crafting a well structured and readable summary.\n
    Summary: {summary}\n
    SUMMARY IN MARKDOWN:
    """
)

all_in_one_prompt = ChatPromptTemplate.from_template(
    """
    You are an excellent executive assistance. You are given a machine-generated transcript of a hybrid video conference:\n
    Use this to create a well structured concise summary from this in Markdown format.\n
    The transcript is not perfect and contains errors. Please ignore those, or try to infer corrections from the context if possible\n
    Key Aspects to focus on in your summary are:\n
    - Clarity and Accuracy: Ensure the summary is clear and accurate, accounting for potential transcription errors.\n
    - Highlight Key Points by emphasizing agreed upon decisions, action items, and dates.\n
    - Organize Efficiently: Use structured sections in the summary.\n
    - Include one section called "Action Items" containing all agreed upon decisions and action items with dates and responsible persons if applicable.\n
    - Keep the summary concise and to the point for efficient future reference of key elements.\n
    - Format: Use Markdown formatting for crafting a well structured and readable summary.\n
    Transcript: {docs}\n
    SUMMARY IN MARKDOWN:
    """
)