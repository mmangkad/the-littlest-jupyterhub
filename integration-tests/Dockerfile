# Systemd inside a Docker container, for CI and local development
ARG BASE_IMAGE=nvcr.io/nvidia/cuda:13.0.2-cudnn-devel-ubuntu24.04
FROM $BASE_IMAGE

# DEBIAN_FRONTEND is set to avoid being asked for input and hang during build:
# https://anonoz.github.io/tech/2020/04/24/docker-build-stuck-tzdata.html
RUN export DEBIAN_FRONTEND=noninteractive \
 && apt-get update \
 && apt-get install --yes \
        systemd \
        bzip2 \
        curl \
        git \
        sudo \
        python3 \
        python3-pip \
        python3-venv \
 && rm -rf /var/lib/apt/lists/*

# Pre-install uv for faster package management during TLJH setup
# This speeds up the bootstrap process significantly
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
 && mv /root/.local/bin/uv /usr/local/bin/uv-bin \
 && chmod +x /usr/local/bin/uv-bin

# Create a wrapper script for uv that automatically uses the TLJH user environment
# - Regular users: uv pip install <pkg> -> installs to ~/.local
# - Admins (sudo): sudo -E uv pip install <pkg> -> installs system-wide to /opt/tljh/user
COPY <<'EOF' /usr/local/bin/uv
#!/bin/bash
# uv wrapper for TLJH - automatically targets the user conda environment
#
# Usage:
#   uv pip install <pkg>        - installs to ~/.local (user-local)
#   sudo -E uv pip install <pkg> - installs system-wide to /opt/tljh/user

# Check if running as root (sudo)
if [[ $EUID -eq 0 ]]; then
    # Running as root/sudo: install system-wide
    exec /usr/local/bin/uv-bin "$@" --python /opt/tljh/user/bin/python
else
    # Regular user: install to user directory for pip install commands
    if [[ "$1" == "pip" && "$2" == "install" ]]; then
        exec /usr/local/bin/uv-bin "$@" --python /opt/tljh/user/bin/python --prefix ~/.local
    else
        exec /usr/local/bin/uv-bin "$@" --python /opt/tljh/user/bin/python
    fi
fi
EOF
RUN chmod +x /usr/local/bin/uv

# Kill all the things we don't need
RUN find /etc/systemd/system \
    /lib/systemd/system \
    -path '*.wants/*' \
    -not -name '*journald*' \
    -not -name '*systemd-tmpfiles*' \
    -not -name '*systemd-user-sessions*' \
    -exec rm \{} \;

RUN systemctl set-default multi-user.target

STOPSIGNAL SIGRTMIN+3

CMD ["/bin/bash", "-c", "exec /lib/systemd/systemd --log-target=journal 3>&1"]
