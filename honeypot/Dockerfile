# Author: Aidan Guenther
FROM python:3.12-slim
RUN pip install --no-cache-dir scapy
WORKDIR /app
COPY . /app
CMD ["python", "-u", "main.py"]