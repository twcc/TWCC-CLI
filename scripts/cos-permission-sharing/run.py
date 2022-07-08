#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import json

s3_keys = {
    'user1': {  # publc cos key
        "ACCESS_KEY": '',
        "SECRET_KEY": ''
    },
    'user2': {  # personal private key
        "ACCESS_KEY": '',
        "SECRET_KEY": ''
    },

}

whom = 'user1'
testing_bkt = 'cus01132'
testing_okey = 'thanks.gif'


class cos_client:
    def __init__(self, whom='user1'):
        self.client = self.get_s3_client_by_user(whom)
        self.my_uid = None

    def get_s3_client_by_user(self, whom='user1'):
        session = boto3.session.Session()
        self.client = session.client(service_name='s3',
                                     aws_access_key_id=s3_keys[whom]['ACCESS_KEY'],
                                     aws_secret_access_key=s3_keys[whom]['SECRET_KEY'],
                                     endpoint_url='https://cos.twcc.ai',
                                     verify=True)
        return self.client

    def get_uid(self):
        if type(self.my_uid) == type(None):
            self.my_uid = self.client.list_buckets()['Owner']['ID']
        return self.my_uid

    def list_objects_by_bucket(self, bucket=""):
        if bucket != "":
            return [x['Key'] for x in self.client.list_objects_v2(Bucket=bucket)['Contents']]

    def get_bucket_policy(self, bucket=""):
        try:
            res = self.client.get_bucket_policy(Bucket=bucket)
            return res
        except Exception as e:
            print(e)

    def share_readonly_to(self, uuid="", bucket=""):
        """
        https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-example-bucket-policies.html
        """
        if uuid != "" and bucket != "":
            bucket_policy = {
                'Version': '2012-10-17',
                'Statement': [{
                    'Sid': 'AddROPerm',
                    'Effect': 'Allow',
                    'Action': [
                        's3:GetObject',
                        's3:GetObjectVersion',
                        's3:ListBucket'],
                    'Resource': [
                        f'arn:aws:s3:::{bucket}/*',
                        f'arn:aws:s3:::{bucket}',
                    ],
                    "Principal": {
                        "AWS": [ "arn:aws:iam:::user/%s"%(uuid) ]
                     },
                }]
            }
            self.client.put_bucket_policy(Bucket=bucket, Policy=json.dumps(bucket_policy))


    def get_obj_in_bucket(self, bucket="", okey=""):
        res = self.client.get_object(Bucket=bucket, Key=okey)
        print(">>> geting object %s: ContentLength=%s, ContentType=%s"%(okey, res['ContentLength'], res['ContentType']))

    def remove_bucket_policy(self, bucket=""):
        if bucket != "":
            self.client.delete_bucket_policy(Bucket=bucket)


s3_user1 = cos_client(whom='user1')
print(s3_user1.get_uid())
print("user1 check %s" % testing_bkt,
      s3_user1.list_objects_by_bucket(bucket=testing_bkt))

s3_user2 = cos_client(whom='user2')
print(s3_user2.get_uid())

s3_user1.share_readonly_to(uuid=s3_user2.get_uid(), bucket=testing_bkt)

print("user2 check %s" % testing_bkt,
      s3_user2.list_objects_by_bucket(bucket=testing_bkt))

s3_user2.get_obj_in_bucket(bucket=testing_bkt, okey=testing_okey)

s3_user1.remove_bucket_policy(bucket=testing_bkt)

print("user2 check %s (no permission)" % testing_bkt)
print(s3_user2.list_objects_by_bucket(bucket=testing_bkt))
