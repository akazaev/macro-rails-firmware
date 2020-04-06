Auto-run Script Setup

1. sudo raspi-config

    Select “Boot Options” then “Desktop/CLI” then “Console Autologin”

2. sudo nano /etc/profile
3. Add:

    sudo /home/pi/macro-stacking-utility/power.py
    
    sudo /home/pi/macro-stacking-utility/run.py &

4. sudo reboot
