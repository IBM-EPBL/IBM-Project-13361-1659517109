FROM python:3.10.4
WORKDIR /app
ADD . /app
COPY requirements.txt /app
RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install ibm_db
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]
