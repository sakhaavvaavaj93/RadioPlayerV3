# Debian 12 (stable) slim - use specific tag for reproducibility
### Multi-stage build: build dependencies in a builder image and copy a virtualenv to a minimal runtime image

FROM python:3.14-slim-trixie AS builder
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

# Install system packages required for building/installing Python packages and tools we need at build time
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    ffmpeg \
    git \
    libavcodec-dev \
    libavformat-dev \
    libffi-dev \
    libogg-dev \
    libopus-dev \
    libsndfile1-dev \
    libssl-dev \
    libswresample-dev \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-venv && \
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
    # Build wheels (including C-extension packages) in the builder so they can be
    # installed in the slim runtime without requiring heavy build toolchains at startup.
    /opt/pyenv/bin/pip wheel --wheel-dir /build/wheels -r /build/requirements.txt && \
    # Ensure common build-time packages (setuptools, wheel) are present in wheels dir
    /opt/pyenv/bin/pip download --no-deps --dest /build/wheels setuptools wheel packaging

# Final runtime image (use official Python slim image)
FROM python:3.14-slim-trixie
ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# Install runtime system packages only (ffmpeg and git required at runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    git \
    libogg0 \
    libopus0 \
    libsndfile1 \
    procps && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /RadioPlayerV3


# Copy application files and built wheels from the builder stage
COPY --from=builder /build /RadioPlayerV3

# venv and dependency installation will be performed at container start time
# by `start.sh` to avoid interpreter/path mismatches across stages and to
# allow installation of packages that require build steps or specific
# system libraries present in the runtime image.

# Ensure startup script is present and executable
COPY --from=builder /build/start.sh /start.sh

# Create a non-root user and give ownership of app files to that user
RUN sed -i 's/\r$//' /start.sh && \
    chmod +x /start.sh && \
    mkdir -p /opt/venv && \
    useradd --create-home --shell /usr/sbin/nologin appuser --uid 1000 && \
    chown -R appuser:appuser /RadioPlayerV3 /opt/venv /start.sh

# Basic healthcheck: ensure the main Python process (main.py) is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD bash -c "pgrep -f main.py >/dev/null || exit 1"

# Run as non-root user
USER appuser

CMD ["/bin/bash", "/start.sh"]
