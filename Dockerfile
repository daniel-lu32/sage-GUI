FROM python:3.12

WORKDIR /usr/src/app

COPY . .

RUN pip install .

CMD sagegui