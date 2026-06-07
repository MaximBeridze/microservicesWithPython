# --- Stage 1: builder ---
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt


# --- Stage 2: runtime ---
FROM python:3.12-slim AS runtime

COPY --from=builder /install /usr/local
WORKDIR /app
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
