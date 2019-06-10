# -*- coding: utf-8 -*-
from __future__ import print_function
import os 
import boto3
import click

from botocore.exceptions import ClientError 
from twcc.clidriver import ServiceOperation
from termcolor import colored
from terminaltables import AsciiTable
from tqdm import tqdm


class S3():
    def __init__(self):
        """ Initilaize information for s3 bucket
        """
        # The setting for connect to s3 bucket
        self.service_name = 's3'
        self.endpoint_url = "s3.twcc.ai"
        self.new_files = []
        self.new_bucket = []
        self.twcc = ServiceOperation()
        self.access_key = self.twcc.def_s3_access_key
        self.secret_key = self.twcc.def_s3_secret_key

        
        # Make sure there are value input here
        if not self.access_key or not self.secret_key:
            raise Exception("No key entered by user")

        session = boto3.session.Session()
        self.s3_cli = session.client(service_name = self.service_name,
                                     aws_access_key_id = self.access_key,
                                     aws_secret_access_key = self.secret_key,
                                     endpoint_url = 'https://' + self.endpoint_url, 
                                     verify=False)

    def list_bucket(self):
        """ Listing all the bucket for S3 directory

            :return            : List all S3 buckets 
        """
        response = self.s3_cli.list_buckets()
        head_data = [bucket_name for bucket_name in response['Buckets'][0].keys()]
        #total_data = [self.c_t(bucket['CreationDate']),self.c_t(str(bucket['Name']).split('.')[0])] if bucket['Name'] in self.new_bucket else [bucket['Name'],str(bucket['CreationDate']).split('.')[0]] for bucket in response['Buckets']]
        total_data = [[str(bucket['CreationDate']).split('.')[0],bucket['Name']] for bucket in response['Buckets']]
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
            tmp = [['Nothing inside the bucket']]
            return tmp
        
    def upload_bucket(self,file_name=None,bucket_name=None,key=None,path=None,r=False):
        """ Upload to S3

            :param file_name         : The name of the upload file 
            :param path              : The path for the files, r must set ot True
            :param bucket_name       : The bucket name
            :param key               : The file name shows inside the bucket
            :param r                 : Setting for recursive
            :return                  : True if success upload file to S3 bucket
        """
        if r == True:
            if os.path.isdir(path):
                on_local_path_len = len("/".join(path.split('/')[:-1])) # Get the len of the local path.
                for root,dirs,files in tqdm(os.walk(path)): # Loop through all the files in the local.
                    for f_name in files:
                        local_file_path = os.path.join(root,f_name) # Get the local file path. 
                        remote_file_path = local_file_path[on_local_path_len + 1:] # Create the key name on S3.
                        try:
                            self.s3_cli.upload_file(local_file_path,bucket_name,remote_file_path)
                        except ClientError as e:
                            print(e)
                            return False
            else:
                print("No such path")
        else:
            try:
                response = self.s3_cli.upload_file(file_name,bucket_name,key)
                print("Successfully upload file : ",key)
            except ClientError as e:
                print(e)
                return False
            return True

    def download_bucket(self,bucket_name=None,key=None,file_name=None,path=None,r=False):
        """ Download from S3

            :param bucket_name       : The bucket name
            :param key               : The file name shows inside the bucket
            :param path              : The path for the files, r must set ot True
            :param file_name         : The name of the download file
            :param r                 : Setting for recursive
            :return            : True if success upload file to S3 bucket
        """
        if r == True:
            # checking for download path exists
            if os.path.isdir(path):
                # get the list of objects inside the bucket
                a = self.list_object(bucket_name)[1:]
                # loop through all the objects
                for i in a:
                    ff_name = os.path.join(path+'/', i[2])
                    check_path = "/".join(ff_name.split('/')[:-1])
                    # check if the download folder exists
                    if not os.path.isdir(check_path):
                        os.mkdir(check_path)
                    # download to the correct path
                    self.s3_cli.download_file(bucket_name,i[2],ff_name)
            else:
                print("No such path")
        else:
            try:
                if not file_name.endswith('/'):
                    check_path = "/".join(file_name.split('/')[:-1])

                print(check_path)
                if not os.path.isdir(check_path):
                    os.mkdir(check_path)

                response = self.s3_cli.download_file(bucket_name,key,file_name)
                print("Successfully download file : ",file_name)
            except ClientError as e:
                print("ERROR during download : ",e)
                return False
            return True


    def create_bucket(self,bucket):
        """ Create an S3 bucket

            :param bucket_name: Unique string name
            :return           : True if bucket is created, else False
        """
        try:
            self.s3_cli.create_bucket(Bucket=bucket)
            self.new_bucket.append(bucket)
            print("Successfully create bucket :",self.c_t(bucket))
        except ClientError as e:
            print("ERROR during create : ",e)
            return False
        return True

    def del_bucket(self,bucket_name,y):
        """ Delete a bucket from S3

            :param bucket_name: Unique string name
            :return: True if bucket is deleted, else False
        """
        try:
            a = self.list_object(bucket_name)[1:]
            if y == True:
                for i in a:
                    self.del_object(bucket_name = bucket_name, file_name = i[2])
            res = self.s3_cli.delete_bucket(Bucket = bucket_name)
            print("Successfully delete bucket :",bucket_name)
        except ClientError as e: 
            if e.response['Error']['Code'] == 'BucketNotEmpty':
                error_msg = "{} still has files inside it.".format(e.response['Error']['BucketName'])
                print(error_msg)
            else:
                print(e.response)
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
        except ClientError as e:
            print(e.response)
        return True
            

    def test_table(self,table_data):
        """ Testing showing table
        """
        table = AsciiTable(table_data)
        print(table.table)

    def c_t(self,txt,color="red"):
        return colored(txt,color)

    def check_4_bucket(self,bucket_name):
        try:
            res = self.s3_cli.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            return False
        return True

    def list_files_v2(self,bucket_name,delimiter='',prefix=''):
        try:
            res = self.s3_cli.list_objects_v2(Bucket=bucket_name,Delimiter=delimiter,Prefix=prefix)
            return [now_dict['Key'] for now_dict in res['Contents']]
            #for now_dict in res['Contents']:
            #    print(now_dict['Key'])
        except ClientError as e:
            return False
        return True
