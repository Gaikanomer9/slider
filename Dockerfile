FROM python:3.9

WORKDIR /app/src

COPY grafonnet-lib /app/grafonnet-lib
COPY OpenSLO /app/OpenSLO

COPY slider /app/src/slider
COPY requirements.txt /app/src
COPY setup.py /app/src

RUN ["pip", "install" , "--no-cache-dir", "-r", "requirements.txt"]
RUN ["pip", "install", "."]
RUN ["rm", "-rf", "/app/src"]

WORKDIR /app/workdir

ENTRYPOINT ["slider"]


