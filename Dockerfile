FROM python:3.12-alpine

WORKDIR /app

ADD requirements.txt .
ADD pyproject.toml .
ADD src src

RUN apk add postgresql-dev

RUN pip install -r requirements.txt

RUN pip install -e .

ENTRYPOINT ["ebms_analytics"]
