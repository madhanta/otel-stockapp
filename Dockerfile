# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies
#RUN apt-get update && apt-get install -y build-essential

# Copy project files
COPY requirements.txt requirements.txt
COPY app.py app.py

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose necessary ports
EXPOSE 8501 8000

# Start Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
