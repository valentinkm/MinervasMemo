# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim


# Set the working directory in the container
WORKDIR /usr/src/app

# Install GitHub CLI
RUN apt-get update && \
    apt-get install -y git gh jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file into the container at /usr/src/app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy source code into container
COPY converter.py .
COPY map_reduce_prompts_minimal.py .
COPY minervasmemo.py .
COPY refine_prompts.py .
COPY splitter.py .
COPY summarizer_map.py .
COPY summarizer_refine.py .
COPY tokenizer.py .

# copy shell script and action file
COPY git_operations.sh .
COPY action.yml .

# ensure shell script is executable
RUN chmod +x git_operations.sh

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV OPENAI_API_BASE=https://zitopenai.openai.azure.com/
ENV OPENAI_API_TYPE=azure
ENV OPENAI_API_VERSION=2023-03-15-preview

# --- Models ---
ENV OPENAI_GPT_MAPREDUCE=gpt-3.5-turbo
# ENV OPENAI_GPT_MAPREDUCE=gpt-4
# ENV OPENAI_GPT_MAPREDUCE=gpt-4-1106-preview

ENV OPENAI_GPT_FINAL=gpt-3.5-turbo
# ENV OPENAI_GPT_FINAL=gpt-4
# ENV OPENAI_GPT_FINAL=gpt-4-1106-preview

ENV OPENAI_GPT_ALL_IN_ONE=gpt-3.5-turbo
# ENV OPENAI_GPT_ALL_IN_ONE=gpt-4
# ENV OPENAI_GPT_ALL_IN_ONE=gpt-4-1106-preview

ENV PYTHON_VERSION=3.11
CMD ["/usr/src/app/git_operations.sh"]