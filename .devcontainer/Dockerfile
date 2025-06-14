FROM docker.io/library/python:3.13
RUN apt update && apt upgrade -y && apt install zip unzip curl git -y && python3 -m pip install pipx

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN echo 'PATH="/root/.local/bin:$PATH"' >> ~/.bashrc 

RUN pipx install poethepoet