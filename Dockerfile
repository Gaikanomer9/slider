# STAGE
FROM python:3.9 AS install-reqs
WORKDIR /app/src

RUN python -m venv /app/slider
ENV PATH="/app/slider/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt


# STAGE
FROM python:3.9 AS install-slider
COPY --from=install-reqs /app/slider /app/slider

RUN python -m venv /app/slider
ENV PATH="/app/slider/bin:$PATH"

COPY slider/ ./slider/
COPY setup.py .
RUN pip install .


# FINAL BUILD STAGE
# Notes on base image:
#   - alpine lacks gnu libstdc++, so that's out
#   - slim hopefully is sufficient; if not, we'll need to go back to full near-1G python-3.9
FROM python:3.9-slim
WORKDIR /app/workdir
COPY --from=install-slider /app/slider /app/slider

ENV PATH="/app/slider/bin:$PATH"
ENTRYPOINT ["slider"]

