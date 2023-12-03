FROM python:3.10-slim-buster

WORKDIR /app

COPY . .
RUN pip3 install -r requirements.txt
RUN pip3 install uvicorn

# CMD [ "python3", "-m" , "flask", "--debug", "run", "--host=0.0.0.0", "--port=8080" ]
# CMD ["python", "app.py"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
