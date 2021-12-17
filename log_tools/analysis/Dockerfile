FROM python:3.9.1

ADD . /analyzer
WORKDIR /analyzer

ENV PYTHONPATH='/analyzer'

RUN pip install -r requirements.txt

CMD [ "/bin/bash" ]