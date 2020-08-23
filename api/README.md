# Chat API

## Installation

### Prerequisites

- [Python](https://www.python.org) >= 3.7

All dependencies can be installed via the `setup.py` scripts.

```bash
# clone chatbot api repository
$git clone ...

# create and activate virtual environment (optional)
$virtualenv --python=python3.7 ~/.virtualenvs/api
$source ~/.virtualenvs/api/bin/activate

# install chatbot api
$cd api
$pip install --editable './[dev]'

# run chatbot api
$python3.7 -m api

# test chatbot api
$curl localhost:8080/version
$curl -H "Content-Type: application/json" -X POST -d '{"question": "ahoj", "language": "sk"}' localhost:8080/bot

# test chatbot api CORS
curl -H "Content-Type: application/json" -H "Origin: https://test.cors" -X POST -v -d '{"question": "ahoj", "language": "sk"}' localhost:8080/bot
```

# Running Tests

```bash
$pytest
```

# Docker

### Api

```bash
# build docker image
$docker build -f docker/api/Dockerfile --tag chatbotapi .

# run Chatbot API and expose it on port 8080
$docker run -d -p 8080:8080 --name chatbotapi chatbotapi:latest
```

### Bert

```bash
# build docker image
$docker build -f docker/bert/Dockerfile --tag bert-as-service .

# run bert-as-service
$docker run --name bert -dit -p 5555:5555 -p 5556:5556 -v ./model/multi_cased_L-12_H-768_A-12/:/model -t bert-as-service 1
```
