FROM python:3.9-slim

#RUN apk add --update py3-pip python3

COPY dist/verify_access_autoconf-*.whl pyisva-*.whl /

RUN apt update && apt install -y unzip \
        && pip3 install /pyisva-*.whl \
        && pip3 install /verify_access_autoconf-*.whl \
        && pip3 cache remove "*" \
        && apt clean

CMD ["/usr/local/bin/python", "-m", "verify_access_autoconf"]
