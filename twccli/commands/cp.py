# -*- coding: utf-8 -*-
from __future__ import print_function
import click
from twccli.twcc.services.s3_tools import S3
import os


def upload(source, directory, key, r):
    """Attempt to upload file or directory to bucket

    :param source: source file path
    :type source: string
    :param directory: destination file path
    :type directory: string
    :param key: file name for upload file
    :type key: string
    :param r: is recursive
    :type r: bool
    """
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
    """Download file or directory from bucket

    :param source: Source storage name
    :type source: string
    :param directory: Download to the specific path
    :type directory: string
    :param key: The name of the key to upload to.
    :type key: string
    :param r: Recursively copy entire directories.
    :type r: bool
    """
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
@click.group(help="Upload / Download files")
def cli():
    pass


@click.command(help="‘Upload/Download’ COS (Cloud Object Service) files.")
@click.option('-upload', 'op', flag_value='upload',
               help='Upload files or folders to the bucket.')
@click.option('-download', 'op', flag_value='download',
               help='Download files from the bucket or download the entire bucket.')
@click.option('-src', '--source', 'source', required=True,
               help='Path of the source directory.')
@click.option('-dest', '--destination', 'directory', required=True,
               help='Path of the destination directory.')
@click.option('-filename', '--file-name', 'key',
               help=' Name of the file.')
@click.option('-r', '--recursively', 'recursive',
              is_flag=True,
              help='Recursively copy entire directories.')
def cos(op, source, directory, key, recursive):
    """Command line for upload/download
    :param source: Source storage name
    :type source: string
    :param upload: Upload files or folders to bucket
    :type upload: string
    :param directory: Download to the specific path
    :type directory: string
    :param key: The name of the key to upload to.
    :type key: string
    :param r: Recursively copy entire directories.
    :type r: bool
    """
    if op == 'upload':
        upload(source, directory, key, r=recursive)
    if op == 'download':
        download(source, directory, key, r=recursive)


cli.add_command(cos)


def main():
    cli()


if __name__ == "__main__":
    main()
