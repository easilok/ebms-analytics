FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY pyproject.toml .
COPY src src
COPY resources resources

RUN pip install -r requirements.txt

# RUN pip install -e .

CMD ["ebms_analytics", "--help"]
