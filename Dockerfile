# ---- Base image ----
FROM python:3.10-slim

# ---- System deps ----
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Working directory ----
WORKDIR /app

# ---- Install Python deps ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy app code ----
COPY . .

# ---- Expose port ----
EXPOSE 8000

# ---- Run app ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
