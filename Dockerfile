# Start with a standard Python base image (using Python 3.10, which is common)
FROM python:3.10-slim-bookworm

# Install the system dependencies from apt
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Set the entry point to run Streamlit
ENTRYPOINT ["streamlit", "run", "app.py"]
