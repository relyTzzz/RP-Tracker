# RP-Tracker
Apex Legends RP Tracker (Stream Overlay)

You will need to request an API key from https://www.apexlegendsapi.com/ and use it to replace the string in line 11 that currently says 'ENTER API KEY HERE'.

Current version (beta) only supports Apex players on PC. User will have to search for Origin user ID either in the application, or on https://www.apexlegendsstatus.com/ and enter it directly in the app.

Upon start, the app records your staring Ranked Points and uses it to determine the daily growth/loss so if the app closes it will restart. 

App automatically switches between displaying your current RP and your daily +/-. You can turn this off by setting 'automode' to False in the config.json file.

If you would prefer to turn the wiping animation off when changing displays, set 'animated' to False in the config.

If you would like a pause between displays, effectively removing the overlay from your stream, set 'deadtimeon' to True in the config. You may also set the duration in seconds by adjusting the 'deadtimeduration' setting to the appropriate amount.

If you want the displays to refresh faster or slower, set 'refresh_time' to the appropriate time in seconds inside the config file (default: 30, minimum: 15).
