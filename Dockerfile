FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. credit_decision.proto
CMD ["python", "app.py"]