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
    s3 = S3('s3','MPBVAQPULDHZIFUQITMO','11t63yDVZTlStKoBBxHl35HgUcgMOSNrVYXojO7b','twgc-s3.nchc.org.tw')
    buckets = s3.list_bucket()
    #s3.test_table(buckets)
    #s3.create_bucket('thisistest4')
    #buckets = s3.list_bucket()
    #s3.test_table(buckets)
    #s3.upload_bucket('this_is_test_file.txt','thisistest4','this_is_test_file.txt')
    #s3.upload_bucket('this_is_test_file2.txt','thisistest4','this_is_test_file2.txt')
    files = s3.list_object('thisistest4')
    s3.test_table(files)
    #s3.upload_bucket('/Users/WillyChen/Work/VTR/CLI_BOTO/twcc-cli/src/test','thisistest4','test',True)
    s3.download_bucket('thisistest4','test','/Users/WillyChen/Work/VTR/CLI_BOTO/twcc-cli/src/test',True)
    #files = s3.list_object('thisistest4')
    #s3.test_table(files)
    #s3.del_bucket('thisistest4')

