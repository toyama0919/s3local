from boto3.session import Session
import os
import glob
import shutil

from .logger import get_logger
from .util import Util
from . import constants


class Core:
    def __init__(
        self,
        url,
        root=os.environ.get("S3LOCAL_ROOT") or constants.DEFAULT_S3LOCAL_ROOT,
        aws_profile=None,
        logger=get_logger(),
    ):
        scheme, bucket_name, prefix = Util.get_bucket_and_prefix_from_url(url)
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.recursive = True if prefix.endswith("/") else False

        self.root = os.path.join(root, scheme, bucket_name)
        os.makedirs(self.root, exist_ok=True)
        self.local_path = os.path.join(self.root, prefix)
        self.bucket = (
            (Session() if aws_profile is None else Session(profile_name=aws_profile))
            .resource("s3")
            .Bucket(bucket_name)
        )
        self.logger = logger
        self.download_paths = []

    def list_download_path(self):
        self.download()
        return self.download_paths

    def list_local_path(self, download=False):
        if download:
            self.download()

        # Search cache only without accessing s3
        if self.recursive:
            glob_string = f"{self.local_path}**/*"
            paths = glob.glob(glob_string, recursive=True)
            paths = [x for x in paths if os.path.isfile(x)]  # file only
        else:
            paths = [self.local_path]

        return paths

    def get_local_root(self):
        return self.root

    def get_local_path(self, download=False):
        if download:
            self.download()
        return self.local_path

    def download_file(self, key, dryrun=False, skip_exist=True):
        dst_path = f"{self.root}/{key}"
        dst_dir_path = os.path.dirname(dst_path)
        s3_url = f"s3://{self.bucket_name}/{key}"
        os.makedirs(dst_dir_path, exist_ok=True)
        if os.path.exists(dst_path) and skip_exist:
            self.logger.debug(f"skip already exists in local: {s3_url}")
        else:
            self.logger.debug(f"Copying: {s3_url} > {dst_path}")
            if not dryrun:
                self.bucket.download_file(key, dst_path)
        self.download_paths.append(dst_path)

    def download(self, dryrun=False, skip_exist=True):
        if self.recursive:
            objects = self.bucket.objects.filter(
                Prefix=self.prefix,
            )
            for key in [o.key for o in objects]:
                self.download_file(key, dryrun, skip_exist=skip_exist)
        else:
            self.download_file(self.prefix, dryrun, skip_exist=skip_exist)

    def delete(self):
        self.logger.info(f"delete => s3://{self.bucket_name}/{self.prefix}")
        self.logger.info(f"delete => {self.local_path}")
        if self.recursive:
            shutil.rmtree(self.local_path)
            self.bucket.objects.filter(
                Prefix=self.prefix,
            ).delete()
        else:
            os.remove(self.local_path)
            self.bucket.delete_object(
                Key=self.prefix,
            )

    def upload(self, source_path):
        basename = os.path.basename(source_path)

        if os.path.isfile(source_path):
            if self.prefix.endswith("/"):
                self.upload_file(
                    source_path,
                    f"{self.prefix}{basename}",
                )
            else:
                # change basename
                self.upload_file(source_path, self.prefix)
        elif os.path.isdir(source_path):
            if self.recursive:
                pair = Util.relative_files_from_dir(directory=source_path)
                for abspath, relative_path in pair.items():
                    self.upload_file(abspath, f"{self.prefix}{relative_path}")
            else:
                raise "not implement"

    def upload_file(self, local_path, key):
        # copy local
        dst_path = os.path.join(self.root, key)
        self.logger.info(f"Copying to local: {local_path} => {dst_path}")
        dst_dir_path = os.path.dirname(dst_path)
        os.makedirs(dst_dir_path, exist_ok=True)
        shutil.copyfile(local_path, dst_path)

        # copy s3
        self.logger.info(
            f"Copying to s3: {local_path} => s3://{self.bucket_name}/{key}"
        )
        self.bucket.upload_file(local_path, key)
