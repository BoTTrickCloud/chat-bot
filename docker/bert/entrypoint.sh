#!/bin/sh

# Bert as a Service
# https://github.com/hanxiao/bert-as-service
# If you want to run BaaS on GPU remove `-cpu` option
bert-serving-start -http_port 8125 -num_worker=$1 -cpu -model_dir /model
