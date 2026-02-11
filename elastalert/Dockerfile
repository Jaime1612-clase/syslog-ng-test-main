FROM python:3.12-bullseye

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        ca-certificates \
        libffi-dev \
        libssl-dev \
        python3-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
        libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

RUN git clone https://github.com/jertel/elastalert2.git /opt/elastalert2 \
    && pip install 'elastalert2[webhook]==2.7.0'

WORKDIR /opt/elastalert2

CMD ["elastalert", "--config", "/opt/elastalert2/config/config.yaml"]
