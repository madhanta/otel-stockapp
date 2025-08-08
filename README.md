# sample opentelemetry projects

This project is a simple Streamlit-based stock analytics dashboard that uses OpenTelemetry for tracing and metrics, and exposes Prometheus metrics for monitoring.

## Features

- Fetches real-time stock prices using Yahoo Finance
- Collects tracing and metrics data with OpenTelemetry
- Exposes metrics endpoint for Prometheus on port `8000`
- Runs Streamlit dashboard on port `8501`
- Runs prometheous to scrap those metrics and display on the dashboard
- Developed on MAC with M1 Chip

## Getting Started

### Prerequisites

- Docker installed on your machine

### Build and Run

1. **Clone the repository** and navigate to the project directory.

2. **Switch to the directory where the DockerFile is present and Build the Docker image:**
   ```
   docker build -t otel-stockapp -f DockerFile .
   
   ```

3. **Run the container:**
   ```sh
   docker run -p 8501:8501 -p 8000:8000 otel-stockapp
   docker run -p 9090:9090 \
  -v "$(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml" \
  prom/prometheus
   ```

4. **Access the app:**
   - Streamlit dashboard: [http://localhost:8501](http://localhost:8501)
   - Prometheus metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)

## Configuration

- Edit `requirements.txt` to add or update Python dependencies.
- The main application logic is in `app.py`.

## Ports

- `8501`: Streamlit web UI
- `8000`: Prometheus metrics endpoint

## License

MIT License

---

**Note:** For production use, review and update dependencies and security
