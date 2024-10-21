FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
# ["python3", "-m" ,"flask", "run", "--host=0.0.0.0"]
CMD ["gunicord","--bind", "0.0.0.0:80","app:create_app"]
