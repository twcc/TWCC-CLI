# -*- coding: utf-8 -*-
from __future__ import print_function
import click
from twccli.twcc.services.s3_tools import S3
import os
from twccli.twcc.util import isNone


def upload(source, directory, key, r):
    """Attempt to upload file or directory to bucket

    :param source: local download path
    :type source: string
    :param directory: bucket name
    :type directory: string
    :param key: file name for upload file
    :type key: string
    :param r: is recursive
    :type r: bool
    """

    if os.path.basename(source) == '':
        source = source[:-1]

    s3 = S3()
    # Check for source type
    if isNone(key) == False:
        s3.upload_file(key=key, bucket_name=directory, source=source)
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

    if os.path.basename(directory) == '':
        directory = directory[:-1]

    s3 = S3()
    s3.list_dir(source, directory, downdir)


def download(bkt, localDownloadDir, key, r):
    """Download file or directory from bucket

    :param bkt: bucket name
    :type bkt: string
    :param localDownloadDir: Download to the specific path
    :type localDownloadDir: string
    :param key: The name of the key to upload to.
    :type key: string
    :param r: Recursively copy entire directories.
    :type r: bool
    """

    if os.path.basename(localDownloadDir) == '':
        localDownloadDir = localDownloadDir[:-1]

    s3 = S3()
    if not s3.check_4_bucket(bkt):
        raise Exception("No such bucket name {} exists".format(bkt))

    if isNone(key):
        if os.path.isdir(directory) and not r:
            raise Exception(
                    "{} is path, need to set recursive to True".format(directory))
        # download whole bucket
        s3.download_bucket(bucket_name=source, path=directory, r=r)
    else:

        if key.find('.') > 0:
            # download single file
            s3.download_file(bucket_name=bkt, path=localDownloadDir, key=key)
            return

        if key.endswith('*'):
            files = s3.list_object(bkt)
            prefix_folder = '/'.join(key.split('/')[:-1])
            desire_files = s3.list_files_v2(
                bucket_name=source, delimiter='', prefix=prefix_folder)
            for desire_file in desire_files:
                if not desire_file.endswith('/'):
                    new_directory = localDownloadDir + desire_file
                    s3.download_bucket(file_name=new_directory,
                                       bucket_name=bkt, key=desire_file)
        else:

            if localDownloadDir.endswith('/'):
                localDownloadDir = localDownloadDir + key

            s3.download_bucket(file_name=localDownloadDir,
                               bucket_name=bkt, key=key)

# end original code ===============================================

# Create groups for command
@click.group(help="Upload / Download files")
def cli():
    pass


@click.command(help="‘Upload/Download’ COS (Cloud Object Service) files.")
@click.option('-sync', '--synchronized', 'sync',
              help='to-cos/from-cos')
@click.option('-dir', '--directory', 'dir', default='./',
              help='Path of the source directory.')
@click.option('-okey', '--object-key', 'key',
              help='File in Cloud.')
@click.option('-fn', '--file-name', 'file',
              help='Files for uploading from local site.')
@click.option('-bkt', '--bucket-name', 'bkt',
              help='Upload files or folders to the bucket.')
def cos(sync, dir, key, file, bkt):
    """Command line for upload/download
    :param bkt: Bucket Name.
    :type bkt: string
    :param dir: Directory in local site
    :type dir: string
    :param key: Download to the specific path
    :type key: string
    :param file: Files for uploading from local site
    :type file: string
    """
    # cp cos -bkt b_name -dir local_dir key key fn filename -sync to-cos/from-cos
    r = False

    if sync == 'from-cos':
        if key.find('.') > 0:
            r = False
        else:
            r = True
    else:
        if isNone(file):
            r = True

    if sync == 'to-cos':
        upload(dir, bkt, file, r)
        return

    if sync == 'from-cos':
        if key.find('.') > 0:
            download(bkt=bkt, localDownloadDir=dir, key=key, r=r)
        else:
            downloadDir(bkt, dir, key)
        return

    print('[Wrong Sync type]: please enter synchronized type : `to-cos` or `from-cos`')
    return


cli.add_command(cos)


def main():
    cli()


if __name__ == "__main__":
    main()
