import boto3

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
testing_bkt = 'zzzzz_aug_cli'
testing_okey = 'README.md'


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

    def get_bucket_acl(self, bucket=""):
        return self.client.get_bucket_acl(Bucket=bucket)

    def share_readonly_to(self, uuid="", bucket=""):
        """
        put object acl, https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html?highlight=put_object_acl#S3.Client.put_object_acl

        permission details https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#CannedACL
        selected acl:
        - authenticated-read
        - public-read
        """
        if uuid != "" and bucket != "":
            existing_ids = self._parse_id_in_acl(
                self.get_bucket_acl(bucket)['Grants'])

            if not uuid in existing_ids:
                existing_ids.append(uuid)
            grant_read = ",".join(["id=\"%s\"" % x for x in existing_ids])
            self.client.put_bucket_acl(
                Bucket=testing_bkt,
                GrantRead=grant_read,
            )

    def _parse_id_in_acl(self, grants):
        return [x['Grantee']['ID'] for x in grants]

    def remove_readonly_to(self, uuid="", bucket=""):
        if uuid != "" and bucket != "":
            existing_ids = self._parse_id_in_acl(
                self.get_bucket_acl(bucket)['Grants'])

            exclu_ids = [x for x in existing_ids if x != uuid]
            grant_read = ",".join(["id=\"%s\"" % x for x in exclu_ids])
            print(grant_read)
            self.client.put_bucket_acl(
                Bucket=testing_bkt,
                GrantRead=grant_read,
            )


s3_user1 = cos_client(whom='user1')
print(s3_user1.get_uid())
print("user1 check %s" % testing_bkt,
      s3_user1.list_objects_by_bucket(bucket=testing_bkt))

s3_user2 = cos_client(whom='user2')

s3_user1.share_readonly_to(uuid=s3_user2.get_uid(), bucket=testing_bkt)

print("user2 check %s" % testing_bkt,
      s3_user2.list_objects_by_bucket(bucket=testing_bkt))

s3_user1.remove_readonly_to(uuid=s3_user2.get_uid(), bucket=testing_bkt)

print("user2 check %s (no permission)" % testing_bkt)
print(s3_user2.list_objects_by_bucket(bucket=testing_bkt))
