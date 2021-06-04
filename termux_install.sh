# This is for Termux only
echo Cynics install for Termux
echo Written by @Beast_boy_shubu
echo Beginning dependency installation in 5 seconds....
#!/bin/bash
sleep 5
apt update
apt install nano clang curl git libcrypt libffi libiconv libjpeg* libjpeg-turbo libwebp libxml2 libxslt make ndk-sysroot openssl postgresql python readline wget zlib -y
git clone https://github.com/Aruoto/Cynics.git
cd Cynics
pip install --upgrade pip setuptools
pip install -r requirements.txt
mv sample.config.ini config.ini
echo Done.
echo Now edit config.ini with nano or anything you want, then run the userbot with python3 -m Cynics.
echo Good luck!
