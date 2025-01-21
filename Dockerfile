FROM python:3.9-slim

#RUN apk add --update py3-pip python3

COPY dist/ibmvia_autoconf-*.whl pyivia-*.whl /

#RUN apt update && apt install -y unzip \
#        && pip3 install /pyivia-*.whl \
#        && pip3 install /ibmvia_autoconf-*.whl \
#        && pip3 cache remove "*" \
#        && apt clean

RUN apt update && apt install -y unzip python3-pip \
    && pip3 install ibmvia_autoconf


CMD ["/usr/local/bin/python", "-m", "ibmvia_autoconf"]
