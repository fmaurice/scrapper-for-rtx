# scrapper-for-rtx
Check if a RTX 3080 is in stock on some french websites :)
To use in a cron job

This script is intended to use on a linux server.
It needs Chrome and Selenium driver installed.

For installing on a Debian platform:
## Installing Chrome
```bash
sudo apt install -y libxss1 libappindicator1 libindicator7
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```
## Installing ChromeDriver
This linux version of chromedriver is patched to avoid detection (see https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver/41220267#41220267)
To get the original file :
```bash
wget https://chromedriver.storage.googleapis.com/2.30/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
```
