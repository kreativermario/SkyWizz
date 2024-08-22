# Use Ubuntu image
FROM ubuntu:latest

# Install necessary packages including traceroute
RUN apt-get update && apt-get install -y traceroute python3 python3-pip

# Set the timezone to Europe/Lisbon
RUN ln -fs /usr/share/zoneinfo/Europe/Lisbon /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

# Set work dir
WORKDIR /skywizz

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Copy the rest of the workspace
COPY . .

# Run the bot
CMD ["python3", "SkyWizz.py"]
