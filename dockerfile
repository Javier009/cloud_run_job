# Use a Python base image us-central1-docker.pkg.dev/real-time-data-pipeline-457520/cloud-run-source-deploy
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file (if you have one, otherwise create an empty one)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your Python script
COPY read_json_files.py .

# Set the command to run your script
CMD ["python3", "read_json_files.py"]

# Should run gcloud auth login first
# gcloud auth configure-docker
# Docker build command that matches GCP : docker build --platform linux/amd64 -t gcr.io/real-time-data-pipeline-457520/read-json-files-from-bucke .
# Docker push image command: docker push gcr.io/real-time-data-pipeline-457520/read-json-files-from-bucke:latest
# gcloud run jobs update json-mapping --image gcr.io/real-time-data-pipeline-457520/read-json-files-from-bucke --region us-central1