#!/usr/bin/bash

sudo systemctl stop mysql
sudo apt remove --purge mysql-server mysql-client mysql-common mysql-server-core-* mysql-client-core-*
sudo apt autoremove
sudo apt autoclean
sudo rm -rf /etc/mysql /var/lib/mysql /var/log/mysql
sudo deluser mysql
sudo delgroup mysql
sudo apt update
