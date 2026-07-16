FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Render uses the PORT environment variable
EXPOSE $PORT

# Gunicorn with Eventlet worker for Flask-SocketIO
CMD gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app
