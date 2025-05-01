# Base image with Python 3.13
FROM python:3.13-slim

# Set working directory inside the container
WORKDIR /app

# Copy the Python script and .env file into the container
COPY app/ /app/

# Install uv and your required Python libraries (fastmcp, httpx)
RUN pip install --no-cache-dir uv
RUN uv pip install --system fastmcp httpx requests mcp overpy geopy pydantic pydantic-ai

# Expose the port that will be used (can also be set via the .env file)
EXPOSE 8000

# Set the command to run the application
CMD ["sh", "-c", "fastmcp run --transport sse server.py"]
