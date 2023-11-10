# Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.11-slim


# Set the working directory in the container
WORKDIR /usr/src/app

# Install GitHub CLI
RUN apt-get update && \
    apt-get install -y git && \
    apt-get install -y gh && \
    apt-get clean

# Copy the requirements.txt file into the container at /usr/src/app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python scripts into the container
COPY converter.py .
COPY map_reduce_prompts.py .
COPY minervasmemo.py .
COPY refine_prompts.py .
COPY splitter.py .
COPY summarizer_map.py .
COPY summarizer_refine.py .
COPY test_summary.py .
COPY tokenizer.py .

# Copy other necessary files such as your shell script and action file
COPY git_operations.sh .
COPY action.yml .

# Ensure your shell script is executable
RUN chmod +x git_operations.sh
# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
# ENV OPENAI_API_BASE=https://zitopenai.openai.azure.com/
# ENV OPENAI_API_TYPE=azure
# ENV OPENAI_API_VERSION=2023-03-15-preview
ENV OPENAI_GPT35_TURBO=gpt-35-turbo
ENV OPENAI_GPT4_TURBO=gpt-4-1106-preview
ENV OPENAI_GPT4=gpt-4
ENV PYTHON_VERSION=3.11

CMD ["/usr/src/app/git_operations.sh"]


