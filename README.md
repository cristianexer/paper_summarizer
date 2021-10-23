# Arxiv Papers Summarizer


## Description

This reposity can deploy a web application that can summarize the papers from arxiv.org along with Apache Tika to extract the text from the pdf files.


## Installation

Launch the services using the following command:
```bash
docker-compose up -d
```


Inspect the services using the following command:
```bash
docker ps
```

```bash
IMAGE                  COMMAND                  CREATED          STATUS          PORTS                    NAMES
paper_summerizer_api   "/app/entrypoint.sh"     7 minutes ago    Up 7 minutes    0.0.0.0:3000->3000/tcp   paper_summerizer-api-1
apache/tika:latest     "/bin/sh -c 'exec ja…"   54 minutes ago   Up 54 minutes   0.0.0.0:9998->9998/tcp   paper_summerizer-tika-1
```


## Usage

Curl

```bash
curl http://localhost:3000/tika\?url\=https://arxiv.org/pdf/2109.11017.pdf
```

There is also an UI that can be used to interact with the service.

URL: `http://localhost:3000`