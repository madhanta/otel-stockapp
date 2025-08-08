# app.py

import threading
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

import logging
from datetime import datetime
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
import time
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server
from collections import deque



# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stock_app")

# --- OpenTelemetry Setup ---
# Tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

# Metrics
prometheus_reader = PrometheusMetricReader()
metrics.set_meter_provider(MeterProvider(metric_readers=[prometheus_reader]))
meter = metrics.get_meter(__name__)
# Start Prometheus metrics HTTP server (default on :8000/metrics)
# Ensure metrics server is started only once
def start_metrics_server():
    try:
        start_http_server(8000)
    except OSError:
        # Metrics server already started
        pass

threading.Thread(target=start_metrics_server, daemon=True).start()

api_duration_metric = meter.create_histogram(
    name="yahoo_api_response_time_ms",
    unit="ms",
    description="Time taken to fetch Yahoo Finance data"
)

stock_price_metric = meter.create_observable_gauge(
    name="stock_price_usd",
    callbacks=[],
    unit="USD",
    description="Latest stock price"
)

# --- Functions ---
def fetch_stock_price(ticker: str):
    with tracer.start_as_current_span("fetch_stock_price"):
        start_time = time.time()
        logger = logging.getLogger("stock_app.fetch_stock_price")
        logger.info(f"Fetching stock price for {ticker}")
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        duration_ms = (time.time() - start_time) * 1000  # duration in ms
        # Record the duration in the histogram
        api_duration_metric.record(duration_ms, attributes={"ticker": ticker})
       
        logger.info(f"Yahoo API call took {duration_ms:.2f} ms")

        if data.empty:
            logger.warning(f"No data returned for {ticker}")
            return None

        price = data["Close"].iloc[-1]
        logger.info(f"Latest price of {ticker}: {price}")
        return price


def plot_stock_chart(ticker: str):
    with tracer.start_as_current_span("plot_stock_chart"):
        logger = logging.getLogger("stock_app.plot_stock_chart")
        logger.info(f"Plotting chart for {ticker}")
        stock = yf.Ticker(ticker)
        data = stock.history(period="5d")
        if data.empty:
            st.warning(f"No chart data found for {ticker}")
            return None
        fig, ax = plt.subplots()
        data["Close"].plot(ax=ax, title=f"{ticker} - Last 5 Days")
        ax.set_xlabel("Date")
        ax.set_ylabel("Close Price (USD)")
        ax.grid(True)
        return fig

def update_metric(price: float):
    stock_price_metric._callbacks.clear()
    stock_price_metric._callbacks.append(lambda options: [metrics.Observation(price, {})])

# --- Streamlit App ---
st.title("📈 Simple Stock Analytics App")
st.markdown("Enter a stock ticker symbol below (e.g., `AAPL`, `GOOG`, `TSLA`)")

ticker = st.text_input("Stock Ticker", value="AAPL")

if ticker:
    with tracer.start_as_current_span("stock_analysis_page"):
        price = fetch_stock_price(ticker)
        if price:
            st.metric(label=f"💵 Current Price of {ticker}", value=f"${price:.2f}")
            update_metric(price)

            chart = plot_stock_chart(ticker)
            
            if chart:
                st.pyplot(chart)

        else:
            st.error("Could not fetch stock price. Please check the ticker symbol.")

# Optional: Delay to allow metric export
time.sleep(2)
# --- End of app.py ---