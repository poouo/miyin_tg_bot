FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN chmod +x /app/scripts/linux/docker/*.sh /app/scripts/linux/local/*.sh || true
RUN mkdir -p /app/data /app/logs

ARG MIYIN_BUILD_REVISION=""
ARG MIYIN_BUILD_BRANCH=main
ARG MIYIN_DOCKER_SOURCE=""
ENV MIYIN_DEPLOYMENT=docker \
    MIYIN_BUILD_REVISION=$MIYIN_BUILD_REVISION \
    MIYIN_BUILD_BRANCH=$MIYIN_BUILD_BRANCH \
    MIYIN_DOCKER_SOURCE=$MIYIN_DOCKER_SOURCE

EXPOSE 9800

CMD ["python", "-m", "apps.runner.main"]
