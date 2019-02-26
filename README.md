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

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py 
sudo python2.7 get-pip.py
sudo pip install pipenv
```

in project directory and try
```
git clone https://github.com/TW-NCHC/TWCC-CLI.git
cd TWCC-CLI/
pipenv install
pipenv run python src/test/gpu_cntr.py
```

del credential file
```
rm -rf ~/.twcc_data/credential
```

Create a default container
```
pipenv run python src/test/gpu_cntr.py create-cntr [-cntr Container name] [-gpu Number of GPU] [-sol Solution Name] [-img Image Name]
                                                   [-s3 S3 bucket name] [-wait Wait for CNTR to ready]
```

List available solutions
```
pipenv run python src/test/gpu_cntr.py list-sol
```

List available images
```
pipenv run python src/test/gpu_cntr.py list-all-img
```

List available cntr
```
pipenv run python src/test/gpu_cntr.py list-cntr [-site Site Id] [-table Show info on table]
```

Remove available cntr
```
pipenv run python src/test/gpu_cntr.py del-cntr -site Site Id
```
