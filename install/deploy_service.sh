#!/bin/bash

SERVICE_FILENAME='slave_takeover_bot.service'
SERVICE_NAME='Slave & takeover Shokh's bot'

SCRIPT_PATH=$(dirname "$(dirname "$(readlink -f "$0")")")


YELLOW='\033[1;33m'
NC='\033[0m' # No Color


echo "${YELLOW}Add ${SERVICE_FILENAME} to path${NC}"

sudo echo "
[Unit]
Description=${SERVICE_NAME}
After=multi-user.target
[Service]
Type=idle
ExecStart=python3 $SCRIPT_PATH/slave_takeover_bot.py
Restart=always
[Install]
WantedBy=multi-user.target" > /etc/systemd/system/${SERVICE_FILENAME}
echo

echo "${YELLOW}Enable ${SERVICE_FILENAME}${NC}"
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_FILENAME}
echo



