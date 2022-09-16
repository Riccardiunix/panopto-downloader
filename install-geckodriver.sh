#!/bin/bash
# Versione modificata di https://askubuntu.com/questions/870530/how-to-install-geckodriver-in-ubuntu
INSTALL_DIR="/usr/local/bin"
wget -q --show-progress "https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz" -O geckodriver.tar.gz
tar -xzf geckodriver.tar.gz && rm geckodriver.tar.gz
chmod +x geckodriver
sudo mv geckodriver "$INSTALL_DIR"
echo "Geckodriver installato in $INSTALL_DIR"
