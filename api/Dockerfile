FROM python:3.9

SHELL ["/bin/bash", "-c"] 

COPY ./ /app

WORKDIR /app

RUN pip3 install -U pip --user

# Install dependencies
RUN pip3 install -r /app/requirements.txt

EXPOSE 3000
