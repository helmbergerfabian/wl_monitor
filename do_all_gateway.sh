#!/usr/bin/env bash
set -e

# start the mosquitto broker
sudo systemctl start mosquitto

# make conda available in THIS shell
source "$HOME/miniconda3/etc/profile.d/conda.sh"

# activate conda env
conda activate wl_monitor

# start the publisher
cd "$HOME/gitrepos/wl_monitor/gateway/src/wl_monitor"
python main_publish.py
