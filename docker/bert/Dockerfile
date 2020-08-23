# Bert as a Service
# https://github.com/hanxiao/bert-as-service
# If you want to run BaaS on GPU use tensorflow/tensorflow:1.12.0-gpu-py3 image
FROM tensorflow/tensorflow:1.12.0-py3

ARG NUM_WORKER
ENV NUM_WORKER=$NUM_WORKER

RUN pip install bert-serving-server[http]
RUN mkdir -p /app
COPY ./docker/bert/entrypoint.sh /app

WORKDIR /app
ENTRYPOINT /app/entrypoint.sh $NUM_WORKER

CMD []
HEALTHCHECK --timeout=5s CMD curl -f http://localhost:8125/status/server || exit 1
