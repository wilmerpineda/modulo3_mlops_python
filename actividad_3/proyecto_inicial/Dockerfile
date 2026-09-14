FROM python:3.11-slim@sha256:db3ff2e1800a8581e2c48a27c3995339d47bdf046da21c7627accd3d51053a93
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry==2.1.3 && poetry config virtualenvs.create false && poetry install --only main --no-root --no-interaction
RUN useradd --create-home --uid 10001 appuser
COPY --chown=10001:10001 src ./src
COPY --chown=10001:10001 data ./data
ENV PYTHONPATH=/app/src BANK_ROOT=/app PYTHONUNBUFFERED=1 EVIDENTLY_DO_NOT_TRACK=1
RUN mkdir artifacts reports && chown -R 10001:10001 /app
USER 10001
RUN python -m bank_ops.cli train --version baseline-v1 && python -m bank_ops.cli promote --version baseline-v1 --actor build --reason bootstrap
EXPOSE 8000
HEALTHCHECK --interval=20s --timeout=3s --start-period=20s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/ready')"
CMD ["uvicorn","bank_ops.api:app","--host","0.0.0.0","--port","8000","--workers","1"]
