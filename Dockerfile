# Debian 12 (stable) slim - use specific tag for reproducibility
### Multi-stage build: build dependencies in a builder image and copy a virtualenv to a minimal runtime image

FROM debian:bookworm-slim AS builder
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

# Install system packages required for building/installing Python packages and tools we need at build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ffmpeg git python3-venv python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy only the files we need from the build context to avoid accidentally including secrets
COPY requirements.txt /build/requirements.txt
COPY start.sh /build/start.sh
COPY main.py config.py user.py utils.py tracing.py /build/
COPY plugins /build/plugins

# Build wheels for dependencies to install in the final runtime image
# Building wheels here avoids compiling in the runtime image and prevents
# copying a venv created on a different base (which can break due to
# differing interpreter paths). Wheels are portable across compatible
# Linux Python runtimes.
RUN python3 -m venv /opt/pyenv && \
    /opt/pyenv/bin/pip install --upgrade pip wheel setuptools && \
    /opt/pyenv/bin/pip wheel --no-deps --wheel-dir /build/wheels -r /build/requirements.txt

# Final runtime image (use official Python slim image)
FROM python:3.14-slim-trixie
ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Install runtime system packages only (ffmpeg is required at runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ffmpeg procps && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /RadioPlayerV3


# Copy application files and built wheels from the builder stage
COPY --from=builder /build /RadioPlayerV3

# Create virtualenv in the runtime image and install dependencies from wheels
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    if [ -d /RadioPlayerV3/wheels ]; then \
    /opt/venv/bin/pip install --no-index --find-links=/RadioPlayerV3/wheels -r /RadioPlayerV3/requirements.txt; \
    else \
    /opt/venv/bin/pip install --no-cache-dir -r /RadioPlayerV3/requirements.txt; \
    fi

# Ensure startup script is present and executable
COPY --from=builder /build/start.sh /start.sh
RUN sed -i 's/\r$//' /start.sh && chmod +x /start.sh

# Create a non-root user and give ownership of app files to that user
RUN useradd --create-home --shell /usr/sbin/nologin appuser --uid 1000 && \
    chown -R appuser:appuser /RadioPlayerV3 /opt/venv /start.sh

# Basic healthcheck: ensure the main Python process (main.py) is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD bash -c "pgrep -f main.py >/dev/null || exit 1"

# Run as non-root user
USER appuser

CMD ["/bin/bash", "/start.sh"]
