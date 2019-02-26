sudo sed -i 's/nova\.clouds\./tw./g' /etc/apt/sources.list
sudo apt update
sudo apt -y install build-essential python2.7 python2.7-dev

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py 
sudo python2.7 get-pip.py
sudo pip install pipenv
