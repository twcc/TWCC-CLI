# TWCC-CLI Customized Image Tutorial
**Here we will show how to use TWCC-CLI to request for customed image and create a new container base on the image.**


## Request for customized image
- **Usage**
    ```bash
    pipenv run python src/test/gpu_cntr.py create-commit
    ```

- **Example** 

    **1. Request for customized image using 246709 image** 
    
    ![image alt](https://snag.gy/MKEhTj.jpg)

## List out ALL customized image requests
- **Usage**
    ```bash
    pipenv run python src/test/gpu_cntr.py list-commit
    ```
    
## Create new container base on the customed image
- **Usage**
    ```bash
    # We can use list-all-imgs to get the Image name and solution name.
    pipenv run python gpu_cntr.py create-cntr -img <Custom Image Name> -sol <Solution Name>
    ```

- **Example** 

    **1. Create a container base on customized image** 
    ```bash
    pipenv run python gpu_cntr.py create-cntr -img copyofimg:latest -sol 自定義影像檔
    ```
