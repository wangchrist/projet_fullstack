FROM python:3.10-slim-buster

WORKDIR /app

COPY . .
RUN pip3 install -r requirements.txt
RUN pip3 install uvicorn
# RUN chmod -R 755 /app/templates

# CMD [ "python3", "-m" , "flask", "--debug", "run", "--host=0.0.0.0" ]
# CMD ["python", "app.py"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
