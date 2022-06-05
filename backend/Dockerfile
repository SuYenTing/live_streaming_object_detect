FROM python:3.7
RUN mkdir /backend
WORKDIR /backend
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8765
CMD ["python3", "server.py"]