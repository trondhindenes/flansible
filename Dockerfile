FROM python:2.7-alpine

WORKDIR /app
COPY ./Flansible/requirements.txt requirements.txt

RUN echo '* Installing OS dependencies' \
  && apk add --update --no-cache \
    curl \
    openssh-client \
    tar \
    build-base \
    libffi-dev \
    openssl-dev \
    python-dev \
    libxml2-dev \
    libxslt-dev \
  && echo '* Installing Python dependencies' \
  && pip install --upgrade pip \
  && pip install -r requirements.txt \
  && echo '* Removing unneeded OS packages' \
  && apk del \
    build-base \
    libffi-dev \
    openssl-dev \
    python-dev

COPY ./Flansible ./

RUN adduser -D -H flansible flansible
USER flansible
