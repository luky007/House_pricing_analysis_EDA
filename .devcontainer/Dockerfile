FROM debian:bookworm-20240110-slim
RUN apt-get update && apt-get -y upgrade \
  && apt-get install -y --no-install-recommends \
    git \
    wget \
    g++ \
    ca-certificates \
    xz-utils \
    libcairo2 libcairo2-dev \
    tldr \
    npm \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b -u -f -p $HOME/miniconda3 \
    && rm -f Miniconda3-latest-Linux-x86_64.sh \
    && conda init bash  \
    && . /root/.bashrc \
    && npm i -g @slidev/cli

COPY environment.yml* .devcontainer/noop.txt /tmp/conda-tmp/
RUN if [ -f "/tmp/conda-tmp/environment.yml" ]; \
    then umask 0002 \
    && conda env update -n base -f /tmp/conda-tmp/environment.yml \
    && rm -rf /tmp/conda-tmp; fi
RUN echo 'echo -e "\e[1;31m Run: poetry install --no-root for installing dependencies \e[0m"' >> $HOME/.bashrc
