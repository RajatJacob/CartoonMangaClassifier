# app/Dockerfile

FROM python:3.10-slim

WORKDIR /app

ADD . .


RUN pip3 install uv
RUN uv venv
RUN uv sync requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
