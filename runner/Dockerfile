# Build from the upstream repository root:
# docker build -f runner/Dockerfile -t rahp-evaluation-runner:local .
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/rahp
COPY requirements.txt /opt/rahp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r requirements.txt
COPY . /opt/rahp
RUN useradd --create-home --uid 10001 rahp && mkdir -p /evaluations && chown rahp:rahp /evaluations
USER rahp
ENTRYPOINT ["python3", "-m", "runner.service"]
CMD ["validate", "--config", "runner/examples/dtg-service.yaml"]
