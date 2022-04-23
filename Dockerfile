FROM python:3.8

RUN pip install pipenv

ADD . /flask-deploy

WORKDIR /flask-deploy

RUN pipenv install --system --skip-lock

RUN useradd -ms /bin/bash celery

EXPOSE 5001

CMD gunicorn --worker-class gevent --workers 8 --bind 0.0.0.0:5001 wsgi:app --max-requests 10000 --timeout 5 --keep-alive 5 --log-level info