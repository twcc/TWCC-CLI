from termcolor import colored
from terminaltables import AsciiTable
from tqdm import tqdm

import boto3
import click
import os 

class S3():
    def __init__(self,service_name='s3',access_key=None,secret_key=None,endpoint_url=None):
        """ Initilaize information for s3 bucket
            :param service_name: Service name of the connection
            :param access_key  : S3 bucket's access key
            :param secret_key  : S3 bucket's secret key
            :param endpoint_url: S3 bucket's endpoint
            :return            : None """
        # The setting for connect to s3 bucket
        self.service_name = service_name
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url
        self.new_files = []
        self.new_bucket = []
        
        # Make sure there are value input here
        if not self.access_key or not self.secret_key:
            raise Exception("No key entered by user")

        session = boto3.session.Session()
        self.s3_cli = session.client(service_name = self.service_name,
                                     aws_access_key_id = self.access_key,
                                     aws_secret_access_key = self.secret_key,
                                     endpoint_url = 'http://' + self.endpoint_url)

    def list_bucket(self):
        """ Listing all the bucket for S3 directory

            :return            : List all S3 buckets 
        """
        response = self.s3_cli.list_buckets()
        head_data = [bucket_name for bucket_name in response['Buckets'][0].keys()]
        total_data = [[self.c_t(bucket['Name']),self.c_t(str(bucket['CreationDate']).split('.')[0])] if bucket['Name'] in self.new_bucket else [bucket['Name'],str(bucket['CreationDate']).split('.')[0]] for bucket in response['Buckets']]
        total_data.insert(0,head_data)
        return total_data

    def list_object(self,bucket_name):
        """ Listing all the file insife of S3 bucket.

            :param bucket_name : Unique string name
            :return            : List all object inside of S3 bucket. 
        """
        res = self.s3_cli.list_objects(Bucket=bucket_name)
        tmp = []
        if 'Contents' in res.keys():
            head_data = [bucket_name for bucket_name in res['Contents'][0].keys() if bucket_name not in ('ETag','Owner')]
            for num in range(len(res['Contents'])):
                tmp_list = [res['Contents'][num][x] if x != 'LastModified' else str(res['Contents'][num][x]).split('.')[0] for x in head_data]
                tmp.append(tmp_list)
            tmp.insert(0,head_data)       
            return tmp
        else:
            print("Nothing inside this bucket")
        
    def upload_bucket(self,file_name,bucket_name,key,r=False):
        """ Upload to S3

            :param file_name         : The name of the upload file or path(r need to set as True)
            :param bucket_name       : The bucket name
            :param key               : The file name shows inside the bucket
            :param r                 : Setting for recursive
            :return                  : True if success upload file to S3 bucket
        """
        if r == True:
            if os.path.isdir(file_name):
                for root,dirs,files in os.walk(file_name):
                    for f in tqdm(files):
                        fullpath = os.path.join(root,f)
                        self.s3_cli.upload_file(fullpath,bucket_name,f)
            else:
                print("No such path")
        else:
            try:
                response = self.s3_cli.upload_file(file_name,src,dist)
                print("Successfully upload file : ",file_name)
            except:
                print("ERROR during upload")
                return False
            return True

    def download_bucket(self,bucket_name,key,file_name,r=False):
        """ Download from S3

            :param bucket_name       : The bucket name
            :param key               : The file name shows inside the bucket
            :param file_name         : The name of the download file name or path(r need to set as True)
            :param r                 : Setting for recursive
            :return            : True if success upload file to S3 bucket
        """
        if r == True:
            a = self.list_object(bucket_name)[1:]
            for i in tqdm(a):
                self.s3_cli.download_file(bucket_name,i[0],'test/'+i[0])
        else:
            try:
                response = self.s3_cli.download_file(bucket_name,key,file_name)
                print("Successfully download file : ",file_name)
            except:
                print("ERROR during download")
                return False
            return True


    def create_bucket(self,bucket):
        """ Create an Amazon S3 bucket

            :param bucket_name: Unique string name
            :return           : True if bucket is created, else False
        """
        try:
            self.s3_cli.create_bucket(Bucket=bucket)
            self.new_bucket.append(bucket)
            print("Successfully create bucket :",self.c_t(bucket))
        except:
            print("ERROR during create")
            return False
        return True

    def del_bucket(self,bucket_name):
        """ Delete a bucket from S3

            :param bucket_name: Unique string name
            :return: True if bucket is deleted, else False
        """
        try:
            a = self.list_object(bucket_name)[1:]
            for i in a:
                self.del_object(bucket_name = bucket_name, file_name = i[0])
            res = self.s3_cli.delete_bucket(Bucket = bucket_name)
            print("Successfully delete bucket :",bucket_name)
        except: 
            print("ERROR during delete bucket")
            return False
        return True 
    
    def del_object(self,bucket_name,file_name):
        """ Delete a file from S3

            :param bucket_name: Unique string name
            :param file_name  : Unique string name
            :return           : True if object is deleted, else False
        """
        try:
            res = self.s3_cli.delete_object(Bucket = bucket_name,
                                            Key = file_name)
            print("Successfully delete object :",file_name)
        except:
            print("ERROR during delete object")
            return False
        return True
            

    def test_table(self,table_data):
        """ Testing showing table
        """
        table = AsciiTable(table_data)
        print(table.table)

    def c_t(self,txt,color="red"):
        return colored(txt,color)

