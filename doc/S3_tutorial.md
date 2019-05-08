# TWCC-CLI S3 tutorial
**Here we will show how to use TWCC-CLI to perform some of the S3 functions.**

##### Table of Contents
[Create new bucket](#createnew)<br>
[List all bucket](#listallbucket)<br>
[List all files in a bucket](#listfilesinbucket)<br>
[Delete file in a bucket](#delfileinbucket)<br>
[Upload](#upload)<br>
[Download](#download)<br>
[Delete bucket](#deletebucket)<br>


<h2 name='createnew'>Create new bucket</h2>

- **Usage**
    ```
    pipenv run python src/test/s3.py create-bucket [-n/--name <Bucket name>] 
    ```
- **Example** 

    **1. Create a new bucket name testbucket** 
    ```
    pipenv run python src/test/s3.py create-bucket -n testbucket 
    ```
    
<h2 name='listallbucket'>List all buckets</h2>

- **Usage**
    ```
    pipenv run python src/test/s3.py list-buckets 
    ```
    
<h2 name='listfilesinbucket'>List all files inside a bucket</h2>

- **Usage**
    ```
    pipenv run python src/test/s3.py del-bucket [-n/--name <Bucket name> [-df]
    ```
- **Example** 

    **1. Show all files inside a bucket** 
    ```
    pipenv run python src/test/s3.py list-files -n wtestbucket
    ```
    
<h2 name='delfileinbucket'>Delete a file inside a bucket</h2>

- **Usage**
    ```
    pipenv run python src/test/s3.py del-file [-n/--name <Bucket name>] [-f/--file_name <Name of the file>]
    ```
- **Example** 

    **1. Show all files inside a bucket** 
    ```
    pipenv run python src/test/s3.py del-file -n wtestbucket -f a.txt
    ```   
    
<h2 name='upload'>Upload a file or a folder to bucket</h2>

- **Usage**
    ```
    pipenv run python src/test/s3.py upload [-s/--source <Local source path>] [-d/--directory <Bucket name>] [-k/--key <file name>] [-r]
    ```
- **Example** 

    **1. Upload a file to bucket** 
    ```
    # if key is not given, the key will be the source file name.
    pipenv run python s3.py upload -s ~/uploadme.txt -d wtestbucket -k downloadme.txt
    ```
    
    **2. Upload a folder to bucket** 
    ```
    # Remember to add -r for recursively copy entire directories.
    pipenv run python s3.py upload -s ~/UploadFolder/ -d wtestbucket -r
    ```

<h2 name='download'>Download a file from bucket</h2>


<h2 name='t'>Delete bucket</h2>

- **Usage**
    ```
    pipenv run python src/test/s3.py del-bucket [-n/--name Bucket name] [-df]
    ```
- **Example** 

    **1. Delete a bucket** 
    ```
    pipenv run python src/test/s3.py del-bucket -n thisiswrong 
    ```
    
    **2. If there are files inside of the bucket, cli will raise error. Therefore, need to add -df to first delete everything inside the bucket**
    ```
    pipenv run python src/test/s3.py del-bucket -n thisiswrong -df
    ```

