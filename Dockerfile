FROM python:3.8.0-slim

WORKDIR /python-support

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y curl --no-install-recommends
COPY ./requirements.txt /python-support/requirements.txt
RUN pip install -r /python-support/requirements.txt
COPY ./scripts /python-support/scripts
COPY ./protobuf /python-support/protobuf
COPY ./cloudstate /python-support/cloudstate
COPY ./setup.py /python-support/setup.py
COPY ./Description.md /python-support/Description.md

RUN /python-support/scripts/fetch-cloudstate-pb.sh master
RUN pip install . -vvv

WORKDIR /
ENTRYPOINT ["python", "-m", "cloudstate.test.tck_services"]

EXPOSE 8080
EXPOSE 8090
