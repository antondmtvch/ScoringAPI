FROM python:3.8

WORKDIR /api

COPY scoring_api scoring_api
COPY main.py main.py

RUN chmod +x main.py

EXPOSE 8080

CMD ["python", "./main.py", "--host", "0.0.0.0", "--log", "score-api.log"]