# Stage 1: Build Python dependencies
FROM python:3.11 AS builder

# Cài gói cần thiết để build gói Python
RUN apt-get update && apt-get install -y build-essential gcc

WORKDIR /install

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.11

# Cài các công cụ CLI cần thiết
RUN apt-get update && apt-get install -y \
    zip \
    tzdata \
    default-mysql-client \
    gnupg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập môi trường
ENV TZ="Asia/Ho_Chi_Minh"
ENV LANG=vi_VN.UTF-8
ENV LC_ALL=vi_VN.UTF-8

# Làm việc ở thư mục này
WORKDIR /kltn-backend

# Copy dependencies đã build ở stage trước
COPY --from=builder /install /usr/local

# Copy source code
COPY . .

EXPOSE 5012

CMD ["gunicorn", "--workers=4", "--threads=1", "--timeout=3600", "--preload", "-b", "0.0.0.0:5012", "server:app"]