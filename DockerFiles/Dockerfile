# Use the base image from tiangolo/nginx-rtmp
FROM tiangolo/nginx-rtmp:latest

LABEL maintainer="Ken Dresdell <kdresdell@gmail.com>"

# Create folders
RUN mkdir -p /nginx
RUN mkdir -p /nginx/hls /nginx/html /nginx/log /nginx/recordings


# Copy your nginx.conf file to the container
COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /nginx/html/index.html


# Set permissions
RUN chmod 777 /nginx/hls /nginx/html /nginx/log /nginx/recordings



# Set the working directory in the container
WORKDIR /nginx/app

# Copy the Flask app code into the container
COPY . .

# Update the package index
RUN apt-get update
RUN apt-get upgrade -y

# Install ffmpeg
RUN apt-get install -y ffmpeg
RUN apt-get install -y nano
RUN apt-get install -y iproute2



# Install python3-pip
RUN apt-get install -y python3-pip


# Install required Python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# Start the RQ worker
# rq worker --url redis://tv.dresdell.com:6379

# CMD ["python3", "myworker.py"]

# Make sure start.sh is executable
RUN chmod +x start.sh
#CMD ["./start.sh"]

# Expose the RTMP and HTTP ports
EXPOSE 1935
EXPOSE 8080
# EXPOSE 5000