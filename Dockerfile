# Use Python image
FROM python:3.12.2

# Set work dir
WORKDIR /skywizz

# Requirements
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy workspace with .dockerignore
COPY . .

CMD ["python", "./SkyWizz.py"]