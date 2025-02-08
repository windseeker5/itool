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

# Install supervisor
RUN apt-get update && \
    apt-get install -y supervisor ffmpeg nano iproute2 python3-pip

# Copy the supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set the working directory in the container
WORKDIR /nginx/app

# Copy the Flask app code into the container
COPY . .

# Install required Python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
#RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt





# Define environment variable
ENV FLASK_APP=app.py

# Expose the RTMP and HTTP ports
EXPOSE 1935
EXPOSE 8080
EXPOSE 5000

# Start supervisor
CMD ["/usr/bin/supervisord"]
