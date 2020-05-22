# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import click
from os.path import relpath, abspath, join, isdir, dirname
from glob import glob
from itertools import chain
from twccli.twcc.services.s3_tools import S3
from twccli.twcc.util import isNone, mkdir_p

def upload(bkt_name, local_dir=None, filename=None):
    twcc_s3 = S3()
    absfn = abspath(filename) if isNone(local_dir) else join(abspath(local_dir), filename)
    okey = relpath(filename) if isNone(local_dir) else join(relpath(local_dir), filename)
    twcc_s3.s3_cli.upload_file(absfn, bkt_name, okey)

def download(bkt_name, dest_fn=None, cos_key=None):
    twcc_s3 = S3()
    mkdir_p(dirname(abspath(dest_fn)))
    twcc_s3.s3_cli.download_file(bkt_name, cos_key, dest_fn)

def list_objects(bucket_name):
    return S3().s3_cli.list_objects_v2(Bucket=bucket_name, MaxKeys=2^31-1)



# end original code ===============================================

# Create groups for command
@click.group(help="Upload / Download files")
def cli():
    pass


@click.command(help="'Upload/Download' COS (Cloud Object Storage) files.")
@click.option('-sync', '--synchronized', 'sync', default = "to-cos",
              help='to-cos/from-cos', show_default=True)
@click.option('-dir', '--directory', 'tdir',
              help='Path of the source directory.')
@click.option('-okey', '--cos-key', 'okey',
              help='File in Cloud.')
@click.option('-fn', '--file-name', 'tfile',
              help='Files for uploading from local site.')
@click.option('-bkt', '--bucket-name', 'bkt',
              help='Upload files or folders to the bucket.')
def cos(sync, tdir, okey, tfile, bkt):
    # cp cos -bkt b_name -dir local_dir key key fn filename -sync to-cos/from-cos

    if not sync in set(['from-cos', 'to-cos']):
        raise click.MissingParameter(param=click.get_current_context().command.params[0])

    if sync == "to-cos":
        if not isNone(tfile):
            upload(bkt_name=bkt, local_dir=tdir, filename=tfile)
        else:
            if isNone(tdir):
                raise click.MissingParameter(param=click.get_current_context().command.params[1])

            for tfile in (chain.from_iterable(glob(join(x[0], '*')) for x in os.walk(tdir))):
                if not isdir(tfile):
                    upload(bkt_name=bkt, filename=tfile)

    if sync == "from-cos":
        if not isNone(okey):
            tdir = abspath(tdir) if not isNone(tdir) else abspath("./")
            absfn = join(abspath(tdir), okey)
            download(bkt, dest_fn=absfn, cos_key=okey)
        else:
            objs =  list_objects(bucket_name=bkt)['Contents']
            for obj in objs:
                okey = obj['Key']
                absfn = join(abspath(tdir), okey)
                download(bkt, dest_fn=absfn, cos_key=okey)


cli.add_command(cos)


def main():
    cli()


if __name__ == "__main__":
    main()
