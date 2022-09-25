FROM python:3.9

WORKDIR /app/src

COPY grafonnet-lib /app/grafonnet-lib
COPY OpenSLO /app/OpenSLO
COPY src /app/src

RUN ["pip", "install" , "--no-cache-dir", "-r", "requirements.txt"]
RUN ["pip", "install", "--editable",  "."]

ENTRYPOINT ["slider"]


