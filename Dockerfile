FROM python:3.13-slim

LABEL Name=Searcharr

WORKDIR /app
ADD . /app

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# -c: log to stdout so `docker compose logs` shows AI/router activity
CMD ["python3", "searcharr.py", "-c"]
