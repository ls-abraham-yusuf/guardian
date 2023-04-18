# syntax=docker/dockerfile:1.2
FROM 809245501444.dkr.ecr.us-east-1.amazonaws.com/release/internal/image/docker-python3.11:latest-main as builder
# Used for non production builds only
ARG EXTRA_INDEX_URLS=""

WORKDIR /app
COPY pyproject.toml poetry.lock* ./
COPY src ./src/

RUN --mount=type=secret,id=pip.conf,dst=/home/worker/.pip/pip.conf,uid=1000 \
  pip install --user --force-reinstall $EXTRA_INDEX_URLS .

FROM 809245501444.dkr.ecr.us-east-1.amazonaws.com/release/internal/image/docker-python3.11:latest-main
COPY --from=builder /home/worker/.local /home/worker/.local


CMD ["python", "-m", "guardian"]
