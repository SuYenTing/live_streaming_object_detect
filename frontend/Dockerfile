FROM python:3.7
RUN mkdir /frontend
WORKDIR /frontend
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python3", "app.py"]