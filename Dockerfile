FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY servers/ servers/
COPY agent/ agent/

RUN pip install --no-cache-dir .

CMD ["python", "-m", "agent", "--dry-run"]
