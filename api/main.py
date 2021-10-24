import logging
import os, json
from fastapi.encoders import jsonable_encoder
import uvicorn, requests
from fastapi import FastAPI, Body, Request, Response
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.templating import Jinja2Templates
# from transformers import pipeline
from bs4 import BeautifulSoup

app = FastAPI(
    title="Summerizer API",
    version="1.0.1"
)

DEBUG = bool(os.getenv('DEBUG', False))

TIKA_URL = os.getenv('TIKA_URL', 'http://localhost:9998/tika/form')

LARGE_BART_MODEL = 'https://api-inference.huggingface.co/models/facebook/bart-large-cnn'

templates = Jinja2Templates(directory="templates")

if DEBUG:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
    logging.basicConfig(level=logging.INFO)

# summarizer = pipeline("summarization")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):

    context = {'request': request}
    
    return templates.TemplateResponse("index.html", context)


@app.post('/summarize')
async def summarize(text_body: Request = Body(...), max_length:int=3000, min_length:int=10):
    # global summarizer
    global LARGE_BART_MODEL

    try:
        text_body = await text_body.body()
        text_body = text_body.decode('utf-8')

        # summary = summarizer(text_body, max_length=max_length, min_length=min_length)

        payload = json.dumps({
                'parameters': {'max_length': max_length, 'min_length': min_length},
                'inputs': text_body
            })

        summary = requests.post(LARGE_BART_MODEL, data=payload).json()

        if len(summary) > 0:
            return Response(content=summary[0].get('summary_text'), status_code=200, media_type='text/plain')
        else:
            return Response(status_code=404)
    except Exception as e:
        return JSONResponse(status_code=500, content=jsonable_encoder({
            'exception': str(e)
        }))



def download_file(url):
    local_filename = url.split('/')[-1]
    local_filename = os.path.join('cache', local_filename)
    if not os.path.exists('cache'):
        os.makedirs('cache')
    # NOTE the stream=True parameter below
    if not os.path.exists(local_filename):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
    return local_filename


@app.get('/tika')
def summarize(url: str, max_length:int=3000, min_length:int=300):
    global TIKA_URL, LARGE_BART_MODEL

    try:
        logging.info(f'Downloading File [url={url}]')
        local_filename = download_file(url)
        # local_filename = os.path.join(os.getcwd(), local_filename)

        logging.info(f'Tika Extracting Text From File [file={local_filename}]')
        files=[('file',(local_filename.split('/')[-1],open(local_filename,'rb'),'application/pdf'))]

        headers = {
            # 'Accept': 'text/plain', 
            # 'User-Agent': 'XY', 'Accept-Encoding': 'gzip, deflate, br'
            }

        tika_response = requests.post(TIKA_URL, headers=headers, files=files)


        if tika_response.status_code == 200:
            logging.info(f'Applying Summarization model[file={local_filename}')
            
            raw_text = tika_response.json()
            raw_text = raw_text.get("X-TIKA:content")
            raw_text = BeautifulSoup(raw_text, 'lxml').select_one('body').text
            # raw_text = tika_response.text

            payload = json.dumps({
                'parameters': {'max_length': max_length, 'min_length': min_length},
                'inputs': raw_text
            })

            summary = requests.post(LARGE_BART_MODEL, data=payload).json()
            
            ### using local model
            # summary = summarizer(tika_response.text, max_length=max_length, min_length=min_length)

            if len(summary) > 0:
                summary = summary[0].get('summary_text')
                return Response(content=summary, status_code=200, media_type='text/plain')
            else:
                return Response(status_code=404)

        else:
            return JSONResponse(status_code=500, content=jsonable_encoder({
                'exception': 'Unable to extract text from file'
            }))

    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content=jsonable_encoder({
            'exception': str(e)
        }))


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=3000, debug=DEBUG, reload=DEBUG)