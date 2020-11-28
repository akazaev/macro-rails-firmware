Auto-run Script Setup

1. sudo raspi-config

    Select “Boot Options” then “Desktop/CLI” then “Console Autologin”

2. sudo nano /etc/profile
3. Add:
    
    sudo /home/pi/macro-rails-firmware/run.py &

4. sudo reboot


Free pins remain on the board.

Free gpio pins: 7, 11.

Reserve gpio pins: 8, 10, 12, 23.
