FROM python:3.9-slim-bullseye

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies:
COPY requirements.txt .
RUN python3.9 -m pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel
RUN python3.9 -m pip install --no-cache-dir \
    -r requirements.txt

# Run the application:
ENV FLASK_APP=app.py
EXPOSE 8050
COPY . .
ARG TOKEN \
    CREDENTIALS
RUN echo $TOKEN > ./google_api_auth/token.json
RUN echo $CREDENTIALS > ./google_api_auth/credentials.json

CMD ["python3", "app.py"]
