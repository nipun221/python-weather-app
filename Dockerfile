FROM python:3.13-slim

# Create a working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
Copy . .

# Default cmd
CMD ["python", "main.py"]