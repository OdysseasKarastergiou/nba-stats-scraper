# Flask Web App

A web application built with Flask.

## Deployment Instructions

### Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python run.py
   ```

### Docker Deployment

1. Build the Docker image:
   ```
   docker build -t flask-web-app .
   ```

2. Run the container locally:
   ```
   docker run -p 8080:8080 flask-web-app
   ```