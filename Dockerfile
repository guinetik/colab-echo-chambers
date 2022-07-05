#https://github.com/cristiangreco/docker-pdflatex
FROM debian:bullseye-20220527-slim
LABEL maintainer="cristian@regolo.cc"

ENV DEBIAN_FRONTEND noninteractive

COPY docker-install.sh /install.sh
RUN sh /install.sh && rm /install.sh

VOLUME ["/sources"]
WORKDIR /sources