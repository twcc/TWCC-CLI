# TWCC-CLI Project

> we cook twcc-cli

requires:
1. build-essential
1. python 2.7
1. python 2.7-dev

## Step 1. scripts for Ubuntu 16.04 @ TWCC

```
sudo sed -i 's/nova\.clouds\./tw./g' /etc/apt/sources.list
sudo apt update
sudo apt -y install build-essential python2.7 python2.7-dev

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py 
sudo python2.7 get-pip.py
sudo pip install pipenv
```

or just run

```
bash tools/twcc_env.sh
```

## Step 2. in project directory and try

```
pipenv install
pipenv run python src/test/gpu_cntr.py
```


## Step 3. Create a default container 

usage:
```
pipenv run python src/test/gpu_cntr.py create-cntr [-cntr Container name] [-gpu Number of GPU] [-sol Solution Name] [-img Image Name]
                                                   [-s3 S3 bucket name] [-wait Wait for CNTR to ready]
```

to create a 1 GPU **Tensorflow** latest environment with name *twcc-cli*

```
pipenv run python src/test/gpu_cntr.py create-cntr 
```


## Step 4. List ALL available solutions

```
pipenv run python src/test/gpu_cntr.py list-sol
```

## Step 5. List ALL available images

```
pipenv run python src/test/gpu_cntr.py list-all-img
```

## Step 6. List container information 

usage:
```
pipenv run python src/test/gpu_cntr.py list-cntr [-site Site Id] [-table Show info on table] [-all Show all container]
```

- example 1: get all containers

```
pipenv run python src/test/gpu_cntr.py list-cntr 
```

- example 2: get a container information with site_id = `93072`

```
pipenv run python src/test/gpu_cntr.py list-cntr -site 93072
```

- example 3: get connection information for site_id = `93072`

```
pipenv run python src/test/gpu_cntr.py list-cntr -site 93072 -table false
```

- example 4: show all container(admin/tenant_admin only)

```
pipenv run python src/test/gpu_cntr.py list-cntr -all
```

This will show your TWCC username, which you gave in [iService](https://iservice.nchc.org.tw/), and SSH access port.


## Step 7. Remove available container

usage:
```
pipenv run python src/test/gpu_cntr.py del-cntr -site Site Id
```

- example 1: delete container with site_id = `93072` 

```
pipenv run python src/test/gpu_cntr.py del-cntr -site 93072
```



## Step 8. delete credential information, just

```
rm -rf ~/.twcc_data
```
