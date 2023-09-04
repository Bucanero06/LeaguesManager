# ------- Builder stage -------
#FROM python:3.11-slim as builder
# Python image to use.
FROM python:3.11-alpine as builder

# Set the working directory in docker
WORKDIR /app

# Install Public Python dependencies
COPY requirements.txt .
RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

## Install private repo
#RUN pip install git+https://${GITHUB_TOKEN}@github.com/Bucanero06/SEC-Client.git



# ------- Final Image stage -------
#FROM python:3.11-slim
FROM python:3.11-alpine as service


# Setting up environment variables for application. Defaults provided for reference.
ENV APP="app:app"
ENV PORT=8000

# Set the working directory
WORKDIR /app

# Copy Python dependencies and app files
COPY --from=builder /usr/local/ /usr/local/
COPY . .

# Command to run on container start using environment variables for configuration
CMD uvicorn $APP --host 0.0.0.0 --port $PORT

# This exposes whatever port the app is set to run on
EXPOSE $PORT




