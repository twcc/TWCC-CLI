# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import click
import threading
import math
import sys
import re
from os.path import relpath, abspath, join, isdir, dirname
from glob import glob
from itertools import chain
from twccli.twccli import pass_environment, logger
from twccli.twcc.services.s3_tools import S3
from twccli.twcc.util import isNone, mkdir_p
from botocore.exceptions import ClientError
from twccli.twcc.services.generic import GenericService


class ProgressPercentage(object):
    def __init__(self, filename, filesize):
        self._filename = filename
        self._size = filesize
        self._seen_so_far = 0
        self._lock = threading.Lock()

        # sys.stdout.write('\n')
    def __call__(self, bytes_amount):
        def convertSize(size):
            if (size == 0):
                return '0B'
            size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
            i = int(math.floor(math.log(size, 1024)))
            p = math.pow(1024, i)
            s = round(size/p, 2)
            return '%.2f %s' % (s, size_name[i])

        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            done = int(50 * self._seen_so_far / self._size)
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r[%s%s] %s  %s / %s  (%.2f%%) " % ('=' * done, ' ' * (50-done),
                                                     self._filename, convertSize(
                                                         self._seen_so_far), convertSize(self._size),
                                                     percentage))
            sys.stdout.flush()


def upload(bkt_name, local_dir=None, filename=None):
    twcc_s3 = S3()
    absfn = abspath(filename) if isNone(
        local_dir) else join(abspath(local_dir), filename)
    okey = relpath(filename) if isNone(
        local_dir) else join(relpath(local_dir), filename)
    # twcc_s3.s3_cli.upload_file(absfn, bkt_name, okey)
    try:
        response = twcc_s3.s3_cli.upload_file(absfn, bkt_name, okey,
                                              Callback=ProgressPercentage(okey, os.stat(absfn).st_size))
        sys.stdout.write('\n')
    except ClientError as e:
        print(str(e))
        raise ClientError


def download(bkt_name, dest_fn=None, cos_key=None):
    twcc_s3 = S3()
    mkdir_p(dirname(abspath(dest_fn)))
    # twcc_s3.s3_cli.download_file(bkt_name, cos_key, dest_fn)
    try:
        response = twcc_s3.s3_cli.download_file(
            bkt_name, cos_key, dest_fn,
            Callback=ProgressPercentage(cos_key, (twcc_s3.s3_cli.head_object(
                Bucket=bkt_name, Key=cos_key))["ContentLength"])
        )
        sys.stdout.write('\n')
    except ClientError as e:
        print(str(e))
        raise ClientError


def list_objects(bucket_name):
    NextMarker = ''
    first_page = {}
    while True:
        res = S3().s3_cli.list_objects(Bucket=bucket_name, Marker=NextMarker)
        if NextMarker == '':
            first_page.update(res)
        else:
            first_page['Contents'].extend(res['Contents'])
        if 'NextMarker' in res:
            NextMarker = res['NextMarker']
        else:
            break
    return first_page
    # return S3().s3_cli.list_objects_v2(Bucket=bucket_name, MaxKeys=2^31-1)


# end original code ===============================================
# Create groups for command
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, help="Upload / Download files")
def cli():
    try:
        ga = GenericService()
        func_call = '_'.join([i for i in sys.argv[1:] if re.findall(
            r'\d', i) == [] and not i == '-sv']).replace('-', '')
        ga._send_ga(func_call)
    except Exception as e:
        logger.warning(e)
    pass


@click.command(help="'Upload/Download' COS (Cloud Object Storage) files.")
@click.option('-sync', '--synchronized', 'sync', type=click.Choice(['to-cos', 'from-cos'], case_sensitive=False), default="to-cos",
              help='to-cos/from-cos', show_default=True)
@click.option('-dir', '--directory', 'tdir',
              help='Path of the source directory.')
@click.option('-okey', '--cos-key', 'okey',
              help='File in Cloud.')
@click.option('-fn', '--file-name', 'tfile',
              help='Files for uploading from local site.')
@click.option('-bkt', '--bucket-name', 'bkt',
              help='Upload files or folders to the bucket.')
@pass_environment
def cos(env, sync, tdir, okey, tfile, bkt):
    # cp cos -bkt b_name -dir local_dir key key fn filename -sync to-cos/from-cos

    if not sync in set(['from-cos', 'to-cos']):
        raise click.MissingParameter(
            param=click.get_current_context().command.params[0])

    if sync == "to-cos":
        if not isNone(tfile):
            upload(bkt_name=bkt, local_dir=tdir, filename=tfile)
        else:
            if isNone(tdir):
                raise click.MissingParameter(
                    param=click.get_current_context().command.params[1])

            for tfile in (chain.from_iterable(glob(join(x[0], '*')) for x in os.walk(tdir))):
                if not isdir(tfile):
                    upload(bkt_name=bkt, filename=tfile)

    if sync == "from-cos":
        if not isNone(okey):
            tdir = abspath(tdir) if not isNone(tdir) else abspath("./")
            absfn = join(abspath(tdir), okey)
            download(bkt, dest_fn=absfn, cos_key=okey)
        else:
            objs = list_objects(bucket_name=bkt)['Contents']
            for obj in objs:
                okey = obj['Key']
                if okey[-1] == '/':
                    continue
                absfn = join(abspath(tdir), okey)
                download(bkt, dest_fn=absfn, cos_key=okey)


cli.add_command(cos)


def main():
    cli()


if __name__ == "__main__":
    main()
