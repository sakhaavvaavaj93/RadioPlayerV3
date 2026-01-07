#!/bin/bash
set -euo pipefail

# If virtualenv doesn't exist, create it and install dependencies
if [[ ! -x /opt/venv/bin/python ]]; then
	echo "Creating virtualenv at /opt/venv and installing dependencies..."
	python3 -m venv /opt/venv
	/opt/venv/bin/pip install --upgrade pip setuptools wheel
	if [[ -d /RadioPlayerV3/wheels ]]; then
		/opt/venv/bin/pip install --find-links=/RadioPlayerV3/wheels -r /RadioPlayerV3/requirements.txt
	else
		/opt/venv/bin/pip install --no-cache-dir -r /RadioPlayerV3/requirements.txt
	fi
fi

# Start the RadioPlayer application using the virtualenv Python
exec /opt/venv/bin/python /RadioPlayerV3/main.py
