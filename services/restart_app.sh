#!/bin/bash

systemctl stop fcscript.service
sleep 1
systemctl start fcscript.service
