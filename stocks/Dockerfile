FROM python:alpine3.17

WORKDIR /app

COPY stocks/requirements.txt .
RUN pip install -r requirements.txt

COPY stocks/portfolio.py .
#COPY .env .

CMD ["flask", "run", "--host=0.0.0.0"]
