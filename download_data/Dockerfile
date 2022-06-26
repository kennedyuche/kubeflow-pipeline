# Define the root docker image to build on
FROM python:3.8-slim

# Define the working directory in docker
WORKDIR /app

# Install the dependencies
RUN pip install -U scikit-learn numpy

# Copy the python script to the working directory in docker
COPY download_data.py .

# Define the entrypoint command to run the python script
ENTRYPOINT [ "python", "download_data.py" ]