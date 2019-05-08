# TWCC-CLI Project

> we cook twcc-cli

INDEX: 
1. [S3](doc/S3_tutorial.md)

## Step 1. Scripts for Ubuntu 16.04 @ TWCC

- **Requirements**

    1. build-essential
    2. python 2.7
    3. python 2.7-dev


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

and you will need to input TWCC API key. 

to get your TWCC API key, you need to [login TWCC Web Portal](https://www.youtube.com/watch?v=jReWylnyBS4)

![TWCC API KEY](https://snag.gy/ZA0xw9.jpg)

and 

![TWCC-CLI key](https://snag.gy/h9itW7.jpg)


## Step 3. Create a Container 

- **Usage**
	```
	pipenv run python src/test/gpu_cntr.py create-cntr [-cntr Container name] [-gpu Number of GPU] [-sol Solution Name] [-img Image Name]
	                                                   [-s3 S3 bucket name] [-wait <Wait for CNTR to ready>]
	```
- **Example**

    **1. Create a container with default configuration** 
       
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
    pipenv run python src/test/gpu_cntr.py list-cntr [-site Site Id] [-table <Show info on table>] [-all <Show all containers>]
    ```

- **Examples**

    **1. Get a list of all containers**

    ```
    pipenv run python src/test/gpu_cntr.py list-cntr 
    ```

    **2. Get a container information with site_id = `93072`**

    ```
    pipenv run python src/test/gpu_cntr.py list-cntr -site 93072
    ```

	**3. Get connection information for site_id = `93072`**
	
	```
	pipenv run python src/test/gpu_cntr.py list-cntr -site 93072 -table False
	```
    
   This will show your TWCC username, which you created in [iService](https://iservice.nchc.org.tw/), and SSH access port.


   **4. Get all containers for a project (admin/tenant_admin only)**
    
    ```
    pipenv run python src/test/gpu_cntr.py list-cntr -all
    ```
	


## Step 7. Remove a container

- **Usage**
    ```
    pipenv run python src/test/gpu_cntr.py del-cntr Site Id
    ```

- **Example** 

    **1. Remove a container with site_id = `93072`** 

    ```
    pipenv run python src/test/gpu_cntr.py del-cntr 93072
    ```



## Step 8. Remove credentials

```
rm -rf ~/.twcc_data
```

## Step ?. Request for customized image
- **Usage**
    ```
    pipenv run python src/test/gpu_cntr.py create-commit
    ```

- **Example** 

    **1. Request for customized image using 246709 image** 
    
    ![image alt](https://snag.gy/MKEhTj.jpg)

## Step ? List out ALL customized image requests
- **Usage**
    ```
    pipenv run python src/test/gpu_cntr.py list-commit
    ```
    
## S3 Step ? Create new bucket
- **Usage**
    ```
    pipenv run python src/test/s3.py create-bucket [-n/--name Bucket name] 
    ```
- **Example** 

    **1. Create a new bucket name testbucket** 
    ```
    pipenv run python src/test/s3.py create-bucket -n testbucket 
    ```
    
## S3 Step ? List out ALL available buckets
- **Usage**
    ```
    pipenv run python src/test/s3.py list-buckets 
    ```
    
## S3 Step ? Delete bucket
- **Usage**
    ```
    pipenv run python src/test/s3.py create-bucket [-n/--name Bucket name] 
    ```
- **Example** 

    **1. Create a new bucket name testbucket** 
    ```
    pipenv run python src/test/s3.py create-bucket -n testbucket 
    ```
