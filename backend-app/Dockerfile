FROM python:3.10-slim
WORKDIR /app
ADD ./backend-app ./backend-app/
ADD ./backend     ./backend/
RUN pip install --no-cache-dir -r backend-app/requirements.txt
EXPOSE 5000
ENV RUN_IN_DOCKER Yes
WORKDIR /app/backend-app
CMD ["python", "app.py"]
