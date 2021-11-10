FROM python:3.9-alpine
LABEL maintainer="Shawn Hu"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD [ "python", "app.py" ]
