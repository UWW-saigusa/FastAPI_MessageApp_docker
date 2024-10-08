FROM python:3.12.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY ./message_app /code/message_app
CMD ["uvicorn", "message_app.main:app", "--host", "0.0.0.0", "--reload", "--port", "8000"]
