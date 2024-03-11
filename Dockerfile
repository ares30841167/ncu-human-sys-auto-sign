# Use an official Python runtime as a parent image
FROM python:3.10.13-alpine

# Set the timezone
ENV TZ="Asia/Taipei"

# Install the necessary library and the compiler
RUN apk add --no-cache libc-dev libpq-dev gcc

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
CMD ["python", "main.py"]