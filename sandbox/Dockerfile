FROM python:3.12-slim
RUN pip install --no-cache-dir pytest==8.3.5
COPY runner.py /opt/codepilot/runner.py
ENV PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
WORKDIR /work
USER 65534:65534
ENTRYPOINT ["python", "-I", "/opt/codepilot/runner.py"]
