from __future__ import print_function
import sys, os
TWCC_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path[1]=TWCC_PATH

from termcolor import colored
def TWCC_LOGO():
    print (
        colored(">"*10+" Welcome to ", 'yellow'),
        colored('TWCC.ai', 'white', attrs=['reverse', 'blink']),
        colored(" "+"<"*10, 'yellow')
    )
TWCC_LOGO() ## here is logo
import re
from twcc.services.s3 import S3

import click,time



if __name__ == '__main__':
    s3 = S3('s3','*','*','*')

    # Create a new bucket
    s3.create_bucket('thisistestbucket')

    # List out all the new bucket
    buckets = s3.list_bucket()
    s3.test_table(buckets)

    # Upload single file to bucket
    s3.upload_bucket(file_name = '/Users/WillyChen/Work/UploadMe.txt',bucket_name = 'thisistestbucket',key = 'DownloadMe.txt')
    # Download single file from bucket 
    s3.download_bucket(bucket_name = 'thisistestbucket',key = 'DownloadMe.txt',file_name = '/Users/WillyChen/Work/DownloadMe.txt')

    # List files inside of bucket
    files = s3.list_object('thisistestbucket')
    s3.test_table(files)

    # Upload files to bucket
    s3.upload_bucket(path = '/Users/WillyChen/Work/UploadFromHere',bucket_name = 'thisistestbucket',r = True)
    # Download files to bucket
    s3.download_bucket(bucket_name = 'thisistestbucket',path='/Users/WillyChen/Work/DownloadToHere',r = True)
    files = s3.list_object('thisistestbucket')
    s3.test_table(files)
    # Delete bucket
    s3.del_bucket('thisistestbucket')

