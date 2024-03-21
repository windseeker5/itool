# Use the base image from tiangolo/nginx-rtmp
FROM tiangolo/nginx-rtmp:latest

LABEL maintainer="Ken Dresdell <kdresdell@gmail.com>"

# Create folders
RUN mkdir -p /nginx
RUN mkdir -p /nginx/hls /nginx/html /nginx/log


# Copy your nginx.conf file to the container
COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /nginx/html/index.html
COPY ken.txt /nginx/html/ken.txt


# Set permissions
RUN chmod 777 /nginx/hls /nginx/html /nginx/log



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


# Install python3-pip
RUN apt-get install -y python3-pip


# Install required Python packages
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# Start the RQ worker
# rq worker --url redis://tv.dresdell.com:6379

# Run the Flask app with gunicorn when the container starts
# gunicorn -w 4 --bind unix:/nginx/app/app.sock app:app

RUN chmod +x start.sh
# CMD ["bash", "start.sh"]


# Expose the RTMP and HTTP ports
EXPOSE 1935
EXPOSE 8080
# EXPOSE 5000

