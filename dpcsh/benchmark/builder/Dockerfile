FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN (echo 'Acquire::http::Proxy "'$http_proxy'";' && echo 'Acquire::https::Proxy "'$https_proxy'";') \
    > /etc/apt/apt.conf.d/00aproxy

RUN apt-get update && apt-get --allow-yes=true -yy install --no-install-recommends --no-install-suggests \
    ca-certificates \
    curl \
    build-essential \
    gccgo-10-multilib-mipsisa64r6-linux-gnuabi64 \
    git \
    && rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin

ENV GO_VER=1.14.4
RUN mkdir -p /opt && cd /opt \
    && curl https://dl.google.com/go/go${GO_VER}.linux-amd64.tar.gz | tar vzxf - \
    && ln -sf $(pwd)/go/bin/* /usr/bin
