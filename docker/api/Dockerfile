FROM python:3.7

# Install packages
RUN apt-get update && apt-get install -y \
  less \
  vim

# Copy source
COPY ./api /app

# Install Chat API
WORKDIR /app
RUN pip3 install .

# Run VApi
CMD ["python3.7", "-m", "api"]
