FROM python:3.12.10-slim

# Install system dependencies for ML libraries
RUN apt-get update && \
    apt-get install -y curl libgomp1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package.json and install Node.js dependencies first for better cache usage
COPY front-end/package.json front-end/

# Remove node_modules if accidentally copied
RUN rm -rf front-end/node_modules

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    cd front-end && npm install

# Copy requirements first for better Docker cache usage
COPY requirements.txt ./

# Install setuptools for pkg_resources and Python dependencies
RUN pip install --no-cache-dir setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copy all other files
COPY . .

# Expose API and React ports
EXPOSE 8080 5173

# Start all services
CMD ["sh", "-c", "python start.py & uvicorn api:app --host 0.0.0.0 --port 8080 & cd front-end && npm run dev"]
