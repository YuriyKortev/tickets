FROM python:3

WORKDIR /server
COPY . .
RUN apt-get update && apt-get install -y libgeos-dev
RUN apt-get install dos2unix

RUN chmod +x ./entrypoint.sh
RUN dos2unix ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]


RUN pip install --upgrade pip
RUN pip install -r requirements.txt



