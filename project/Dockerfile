FROM python:3.8-alpine3.15
LABEL maintainer="Shawn Hu"
COPY ./techtrends/ /techtrends/
WORKDIR /techtrends
RUN pip install -r requirements.txt \
      && python init_db.py
CMD [ "python", "app.py" ]
EXPOSE 3111
