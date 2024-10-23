SERVICE_FILENAME='slave_takeover_bot.service'
INSTALL_PATH=$(dirname "$(readlink -f "$0")")

GREEN='\033[1;32m'
NC='\033[0m' # No Color

echo "${GREEN}Stop service${NC}"
sh ${INSTALL_PATH}/stop_service.sh


echo "${GREEN}Disable service${NC}"
systemctl disable ${SERVICE_FILENAME}

echo "${GREEN}Delete ${SERVICE_FILENAME}${NC}"
rm /etc/systemd/system/${SERVICE_FILENAME}

echo "${GREEN}Daemon-reload ${SERVICE_FILENAME}${NC}"
systemctl daemon-reload