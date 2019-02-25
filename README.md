# TWCC-CLI Project

> we cook twcc-cli

requires:
1. build-essential
1. python 2.7
1. python 2.7-dev

scripts for Ubuntu 16.04 @ TWCC
```
sudo sed -i 's/nova\.clouds\./tw./g' /etc/apt/sources.list
sudo apt update
sudo apt -y install build-essential python2.7 python2.7-dev
```

in project directory and try
```
pipenv install
pipenv run python src/test/gpu_cntr.py
```

del credential file
```
rm -rf ~/.twcc_data/credential
```
