FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
COPY nexus_agent ./nexus_agent
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["uvicorn", "nexus_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
