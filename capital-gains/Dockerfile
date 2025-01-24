FROM python:alpine3.17

WORKDIR /app

COPY capital-gains/requirements.txt .
RUN pip install -r requirements.txt

COPY capital-gains/gains.py .

CMD ["flask", "run", "--host=0.0.0.0"]