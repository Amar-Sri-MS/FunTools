# Use an official Python runtime as a base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /dbgsh

ENV WORKSPACE=/dbgsh

# Copy the current directory contents into the container at /app
COPY . /dbgsh

# Update the package list and install vim
# Needed to edit the dut config file
RUN apt-get update && apt-get install -y vim

# Run setup.py to install the package (also installs dependencies if specified)
RUN python setup.py install

