FROM python:3.13-slim

WORKDIR /code

# ← adicione isto
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8000

COPY main.py ./main.py
COPY app ./app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
