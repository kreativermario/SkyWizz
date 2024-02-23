# Use Python alpine image
FROM python:3.12.2-alpine

# Set work dir
WORKDIR /skywizz

# Requirements
COPY requirements.txt .

# Add C and C++ compiler for matplotlib
RUN apk add --no-cache make gcc g++

# Run cmake
RUN apk add --no-cache cmake

# Install dependencies
RUN pip install -r requirements.txt

# Copy workspace with .dockerignore
COPY . .

CMD ["python", "./SkyWizz.py"]

