# set the base image. Since we're running
# a Python application a Python base image is used
FROM python:2.7-alpine
WORKDIR /usr/src/app
LABEL maintainer="Yeow Teck Keat"
COPY ./techtrends/requirements.txt ./
RUN pip install -r requirements.txt
COPY ./techtrends ./
RUN python init_db.py
RUN pip install -r requirements.txt
EXPOSE 3111
CMD [ "python", "app.py" ]
