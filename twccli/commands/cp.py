# -*- coding: utf-8 -*-
from __future__ import print_function
import click
from twccli.twcc.services.s3_tools import S3
import os
from twccli.twcc.util import isNone


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
    if isNone(source) == False:
        if os.path.basename(source) == '':
            source = source[:-1]

    s3 = S3()
    # Check for source type
    if isNone(source):
        s3.upload_file(key=key, bucket_name=directory)
        return
    if os.path.isdir(source):
        if r != True:
            raise Exception(
                "{} is path, need to set recursive to True".format(source))
        else:
            s3.upload_bucket(path=source, bucket_name=directory, r=r)
    else:

        if isNone(key):
            key = source.split('/')[-1]

        s3.upload_bucket(file_name=source, bucket_name=directory, key=key)


def downloadDir(source, directory, downdir):
    s3 = S3()
    s3.list_dir(source, directory, downdir)


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

        if r != True:
            raise Exception(
                "{} is path, need to set recursive to True".format(directory))
        else:
            # download whole bucket
            s3.download_bucket(bucket_name=source, path=directory, r=r)
    else:

        if key.find('.') > 0:
            # download single file
            s3.download_file(bucket_name=source, path=directory, key=key)
            return

        if key.endswith('*'):
            files = s3.list_object(source)
            prefix_folder = '/'.join(key.split('/')[:-1])
            desire_files = s3.list_files_v2(
                bucket_name=source, delimiter='', prefix=prefix_folder)
            for desire_file in desire_files:
                if not desire_file.endswith('/'):
                    new_directory = directory + desire_file
                    s3.download_bucket(file_name=new_directory,
                                       bucket_name=source, key=desire_file)
        else:

            if directory.endswith('/'):
                directory = directory + key

            s3.download_bucket(file_name=directory,
                               bucket_name=source, key=key)

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
@click.option('-src', '--source', 'source',
              help='Path of the source directory.')
@click.option('-dest', '--destination', 'directory', required=True,
              help='Path of the destination directory.')
@click.option('-fn', '--file-name', 'key',
              help=' Name of the file.')
@click.option('-downdir', '--download-directory', 'downdir',
              help=' the directory which you want to download in cloud.')
@click.option('-r', '--recursively', 'recursive',
              is_flag=True,
              help='Recursively copy entire directories.')
def cos(op, source, directory, key, recursive, downdir):
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
    if isNone(op):
        print("please enter operation : upload/download")
    else:
        if op == 'upload':
            if isNone(key):
                # upload single file
                if isNone(source):
                    print('please enter file name or source directory')
                    return

            upload(source, directory, key, r=recursive)
        if op == 'download':
            if isNone(downdir):
                download(source, directory, key, r=recursive)
            else:
                downloadDir(source, directory, downdir)


cli.add_command(cos)


def main():
    cli()


if __name__ == "__main__":
    main()
