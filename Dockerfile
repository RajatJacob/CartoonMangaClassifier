# app/Dockerfile

FROM python:3.10-slim

WORKDIR /app

ADD . .


RUN pip3 install poetry streamlit tensorflow
RUN poetry install

WORKDIR /app/app

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]