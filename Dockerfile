FROM python:3.9-slim

WORKDIR /opt/syncer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    python3-pip \
    podman \
    fuse-overlayfs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt /opt/syncer
RUN pip3 install --no-cache-dir -r requirements.txt
COPY src/ /opt/syncer/
CMD ["python3", "main.py"]