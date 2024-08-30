#!/bin/bash

sleep 1

cd /home/$USER/repos/Finances_Controller/

sleep 1

streamlit run main.py --server.port 8501
