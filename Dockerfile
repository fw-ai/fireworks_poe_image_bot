# Start with a lightweight version of Ubuntu
FROM ubuntu:22.04

# Set the environment variables
ENV FIREWORKS_API_BASE=""
ENV FIREWORKS_API_KEY=""
ENV GCS_BUCKET_NAME=""
ENV ENVIRONMENT=""
ENV MODEL=""

# Install python3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Upgrade pip
RUN pip3 install --upgrade pip

# Install the required Python packages
RUN pip3 install fastapi-poe==0.0.23 \
    'fireworks-ai>=0.6.0' \
    boto3

WORKDIR /app

COPY ./ /app

RUN pip install .

# Expose the port that your FastAPI app will run on
EXPOSE 80

# The command to run the FastAPI app
CMD ["python3", "-m", "fireworks_poe_image_bot"]
