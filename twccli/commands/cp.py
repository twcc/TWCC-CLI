# -*- coding: utf-8 -*-
from __future__ import print_function
import click
from twcc.services.s3_tools import S3

def upload(source, directory, key, r):
    s3 = S3()
    # Check for source type
    if os.path.isdir(source):
        if r != True:
            print('r != True, directory')
            raise Exception(
                "{} is path, need to set recursive to True".format(source))
        else:
            print('dir upload')
            s3.upload_bucket(path=source, bucket_name=directory, r=r)
    else:

        if key == None:
            key = source.split('/')[-1]

        s3.upload_bucket(file_name=source, bucket_name=directory, key=key)


def download(source, directory, key, r):
    print('enter download')
    s3 = S3()
    if not s3.check_4_bucket(source):
        raise Exception("No such bucket name {} exists".format(source))

    if os.path.isdir(directory) and key == None:
        print('is dir')
        if r != True:
            raise Exception(
                "{} is path, need to set recursive to True".format(directory))
        else:
            s3.download_bucket(bucket_name=source, path=directory, r=r)
    else:
        print('is file')
        if key.endswith('*'):
            files = s3.list_object(source)
            prefix_folder = '/'.join(key.split('/')[:-1])
            desire_files = s3.list_files_v2(
                bucket_name=source, delimiter='', prefix=prefix_folder)
            for desire_file in desire_files:
                if not desire_file.endswith('/'):
                    print('desire_file = '+desire_file)
                    new_directory = directory + desire_file
                    s3.download_bucket(file_name=new_directory,
                                       bucket_name=source, key=desire_file)
        else:

            if directory.endswith('/'):
                directory = directory + key

            print('directory =' + directory)
            s3.download_bucket(file_name=directory,
                               bucket_name=source, key=key)

        print('download end')
# end original code ===============================================

# Create groups for command
@click.group(help="Upload / Download File")
def cli():
    pass


@click.command(help="cos(Cloud Object Service)")
@click.option('-upload', 'op', flag_value='upload',
               help='Upload files or folders to bucket')
@click.option('-download', 'op', flag_value='download',
               help='Download the files in the bucket or the entire bucket')
@click.option('-s', '--source', 'source', required=True,
               help='Source storage name')
@click.option('-d', '--directory', 'directory', required=True,
               help='Download to the specific path')
@click.option('-k', '--key', 'key',
               help='The name of the key to upload to.')
@click.option('-r', 'r', is_flag=True, help='Recursively copy entire directories.')
def o(op, source, directory, key, r):
    if op == 'upload':
        print('enter upload')
        upload(source, directory, key, r=r)
    if op == 'download':
        print('enter download')
        download(source, directory, key, r=r)



cli.add_command(o)




def main():
    cli()


if __name__ == "__main__":
    main()
