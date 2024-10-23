#!/bin/bash

SCRIPT_PATH=$(dirname "$(readlink -f "$0")")

YELLOW='\033[1;33m'
NC='\033[0m' # No Color



echo "${YELLOW}Installing gspread${NC}"
sudo pip3 install gspread
echo
echo

echo "${YELLOW}Installing oauth2client${NC}"
sudo pip3 install oauth2client
echo
echo


echo "${YELLOW}Installing telebot${NC}"
sudo pip3 install pyTelegramBotAPI
echo
echo
