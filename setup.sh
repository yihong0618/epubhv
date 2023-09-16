#!/bin/sh

# Check if the poetry is installed
if
    ! command -v pdm &> /dev/null
then
    echo "PDM could not be found"
    echo "Attempting to Install PDM"

    # Install poetry for python dependency management
    curl -sSL https://pdm.fming.dev/install-pdm.py | python3 -
fi
# Install python dependencies (including development-only ones)
pdm install -d
pdm venv activate