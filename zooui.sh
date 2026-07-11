#!/bin/bash

# Launch ZooUI with the configured conda environment

__conda_setup="$('/home/asd/miniconda3/bin/conda' 'shell.bash' 'hook' 2>/dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/asd/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/home/asd/miniconda3/etc/profile.d/conda.sh"
    fi
fi

CONDA_ENV="ZooUI-Wayland"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec 2>>"$SCRIPT_DIR/launcher.log"
conda run -n "$CONDA_ENV" python "$SCRIPT_DIR/main.py" "$@"

