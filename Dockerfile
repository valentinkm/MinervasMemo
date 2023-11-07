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

# Copy the rest of your project's code into the container
COPY . /usr/src/app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV OPENAI_API_BASE=https://zitopenai.openai.azure.com/
ENV OPENAI_API_TYPE=azure
ENV OPENAI_API_VERSION=2023-03-15-preview
ENV OPENAI_MODEL_NAME_TURBO=gpt-35-turbo
ENV OPENAI_MODEL_NAME_GPT4=gpt-4
ENV OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
ENV OPENAI_EMBEDDING_MODEL_NAME=text-embedding-ada-002
ENV PYTHON_VERSION=3.11

RUN chmod +x /usr/src/app/git_operations.sh

CMD ["/usr/src/app/git_operations.sh"]


