# STAGE: reqs
FROM python:3.9 AS install-reqs
WORKDIR /app/src

RUN python -m venv /app/slider
ENV PATH="/app/slider/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt


# STAGE: slider
FROM install-reqs AS install-slider
WORKDIR /app/src

RUN python -m venv /app/slider
ENV PATH="/app/slider/bin:$PATH"

COPY slider/ ./slider/
COPY setup.py .
RUN pip install .

# Let's be smart about what we make available to the final layer
# TODO: have this part be an easier-maintainable separate build script
RUN mkdir -p /app/justslider/bin
RUN cp -a /app/slider/bin/slider /app/justslider/bin
RUN SITEPKGSDIR="$(echo /app/slider/lib/python*/site-packages|cut -d/ -f 4-44)" && \
    echo $SITEPKGSDIR && \
    mkdir -p /app/justslider/$SITEPKGSDIR && \
    cp -a /app/slider/$SITEPKGSDIR/slider* /app/justslider/$SITEPKGSDIR


# FINAL BUILD STAGE
# Notes on base image:
#   - alpine lacks gnu libstdc++, so that's out
#   - slim hopefully is sufficient; if not, we'll need to go back to the near-1G python:3.9
FROM python:3.9-slim
WORKDIR /app/workdir
COPY --from=install-reqs /app/slider /app/slider
# Just add the <100kB of slider itself
COPY --from=install-slider /app/justslider /app/slider


ENV PATH="/app/slider/bin:$PATH"
ENTRYPOINT ["slider"]

