FROM ubuntu:18.04
ARG UID
ARG GID

# Update the package list, install sudo, create a non-root user, and grant password-less sudo permissions
RUN apt update && \
    apt install -y sudo && \
    addgroup --gid $GID bmcbuild && \
    adduser --uid $UID --gid $GID --disabled-password --gecos "" bmcbuild && \
    echo 'bmcbuild ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

# dpcsh, i2c debug lib on BMC (arm)
RUN apt-get update && apt-get install -qq --yes --no-install-recommends --no-install-suggests \
        gcc-arm-linux-gnueabihf \
        g++-arm-linux-gnueabihf \
        libc6-dev-armel-cross \
	make

# rust
# Get Ubuntu packages
RUN apt-get install -y \
    build-essential \
    curl


# Set the non-root user as the default user
USER bmcbuild

# Set the working directory
WORKDIR /home/bmcbuild

# install rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y

# add toolchain, need cargo path for this
ENV PATH="/home/bmcbuild/.cargo/bin:${PATH}" 
RUN rustup target add armv7-unknown-linux-gnueabihf

# copy file into cargo config
ADD ./config.cargo /home/bmcbuild/.cargo/config

# Copy files into the container and set the appropriate permissions
# COPY --chown=bmcbuild:bmcbuild . /home/bmcbuild/src
# RUN chmod -R 755 /home/bmcbuild

