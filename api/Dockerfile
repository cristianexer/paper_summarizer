FROM python:3.9

COPY . /app

WORKDIR /app

RUN pip3 install -U pip --user

# Install dependencies
RUN pip3 install -r /app/requirements.txt

# RUN chmod +x /app/entrypoint.sh

EXPOSE 3000

ENTRYPOINT [ "/app/entrypoint.sh" ]