FROM python:3.10-slim
WORKDIR /app
ADD . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
ENV RUN_IN_DOCKER Yes
CMD ["python", "app.py"]
