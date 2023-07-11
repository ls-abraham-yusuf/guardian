# syntax=docker/dockerfile:1.3
ARG MODULE_NAME="guardian"
ARG PYTHON_IMAGE=809245501444.dkr.ecr.us-east-1.amazonaws.com/release/internal/image/docker-python3.10:latest-main

FROM ${PYTHON_IMAGE} as builder
WORKDIR /build

# Used to resolve the dependencies and builds the wheel
RUN pip install "poetry==1.2.2"


COPY pyproject.toml poetry.lock ./
RUN --network=none poetry export > ./requirements-frozen.txt

COPY ./src .
RUN --network=none poetry build -f wheel


FROM ${PYTHON_IMAGE} as installer
WORKDIR /build

# Install the dependencies frozen in the previous step and the package itself
# Because we install the frozen dependencies before we don't risk installing unlocked deps
# Also we install the deps and the app in two steps to make use of layer caching
COPY --from=builder /build/requirements-frozen.txt .
RUN --mount=type=secret,id=pip.conf,dst=/home/worker/.pip/pip.conf,uid=1000\
      pip install -r requirements-frozen.txt

COPY --from=builder /build/dist/${MODULE_NAME}-*.whl .
RUN --network=none pip install ./${MODULE_NAME}-*.whl --no-deps


FROM ${PYTHON_IMAGE}

# The runner, which we make separate so that the wheel and the frozen requirements arent part of the final image
COPY --from=installer /home/worker/.local /home/worker/.local

ENV UVICORN_PORT 8888
ENV UVICORN_LOG_LEVEL info

USER 1000
CMD [ "uvicorn", "${MODULE_NAME}:app" ]
#+++++++++++++++






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
