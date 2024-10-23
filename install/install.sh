
INSTALL_PATH=$(dirname "$(readlink -f "$0")")

GREEN='\033[1;32m'
NC='\033[0m' # No Color

echo "${GREEN}Installing modules${NC}"
sh ${INSTALL_PATH}/install_modules.sh

echo "${GREEN}Deploing of service${NC}"
sh ${INSTALL_PATH}/deploy_service.sh

echo "${GREEN}Start of service${NC}"
sh ${INSTALL_PATH}/start_service.sh
echo

sleep 1

echo "${GREEN}Check service${NC}"
sh ${INSTALL_PATH}/check_service.sh
echo