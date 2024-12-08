#!/bin/bash

# Copy the systemd service file to the system directory
sudo cp systemd_service/transcription_app.service /etc/systemd/system/

# Reload the systemd daemon to recognize the new service
sudo systemctl daemon-reload

# Restart the transcription_app service
sudo systemctl restart transcription_app.service
