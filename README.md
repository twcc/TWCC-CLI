# TWCC-CLI Project

> we cook twcc-cli


## Step 1. Scripts for Ubuntu 16.04 @ TWCC

- **Requirements**
    1. build-essential
    1. python 2.7
    1. python 2.7-dev


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

## Step 2. Go into the project directory, and try executing cli program

```
pipenv install
pipenv run python src/test/gpu_cntr.py
```


## Step 3. Create a Container 

- **Usage**
	```
	pipenv run python src/test/gpu_cntr.py create-cntr [-cntr Container name] [-gpu Number of GPU] [-sol Solution Name] [-img Image Name]
	                                                   [-s3 S3 bucket name] [-wait Wait for CNTR to ready]
	```

- **Create a container with default configuration** 
    ```
	pipenv run python src/test/gpu_cntr.py create-cntr 
	```
    
    - Default configuration：
        - Solution & Image: Tensorflow (latest environment)
        - Container name: twcc-cli
        - Hardware: 1 GPU + 4 cores + 90 GB memory
        
        
    

    


## Step 4. List ALL available solutions

```
pipenv run python src/test/gpu_cntr.py list-sol
```

## Step 5. List ALL available images

```
pipenv run python src/test/gpu_cntr.py list-all-img
```

## Step 6. List container information 

- **Usage**
    ```
    pipenv run python src/test/gpu_cntr.py list-cntr [-site Site Id] [-table Show info on table]
    ```

- **Examples**

    1. Get a list of containers

    ```
    pipenv run python src/test/gpu_cntr.py list-cntr 
    ```

    2. Get a container information with site_id = `93072`

    ```
    pipenv run python src/test/gpu_cntr.py list-cntr -site 93072
    ```

	3. Get connection information for site_id = `93072`
	
	```
	pipenv run python src/test/gpu_cntr.py list-cntr -site 93072 -table false
	```
	
     This will show your TWCC username, which you created in [iService](https://iservice.nchc.org.tw/), and SSH access port.


## Step 7. Remove a container

- **Usage**
    ```
    pipenv run python src/test/gpu_cntr.py del-cntr -site Site Id
    ```

- **Example** 

    1. Remove a container with site_id = `93072` 

    ```
    pipenv run python src/test/gpu_cntr.py del-cntr -site 93072
    ```



## Step 8. Remove credentials

```
rm -rf ~/.twcc_data
```
