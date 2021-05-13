from boto3.session import Session
import os
import glob
import shutil
from .logger import get_logger
from .util import Util


DEFAULT_S3LOCAL_ROOT = (
    os.environ.get("S3LOCAL_ROOT") or f"{os.environ.get('HOME')}/.s3local"
)


class Core:
    def __init__(self, url, root=DEFAULT_S3LOCAL_ROOT, logger=get_logger()):
        scheme, bucket_name, prefix = Util.get_bucket_and_prefix_from_url(url)
        self.bucket_name = bucket_name
        self.prefix = prefix
        self.recursive = True if prefix.endswith("/") else False

        self.root = f"{root}/{scheme}/{bucket_name}"
        os.makedirs(self.root, exist_ok=True)
        self.bucket = Session().resource("s3").Bucket(bucket_name)
        self.logger = logger

    def list_local_path(self, download=False):
        if download:
            self.download()

        if self.recursive:
            glob_string = f"{self.root}/{self.prefix}**/*"
        else:
            glob_string = f"{self.root}/{self.prefix}"

        paths = glob.glob(glob_string, recursive=True)
        paths = [x for x in paths if os.path.isfile(x)]
        return paths

    def get_local_root(self):
        return self.root

    def get_local_path(self, download=False):
        if download:
            self.download()
        return f"{self.root}/{self.prefix}"

    def download_file(self, key, dryrun=False, skip_exist=True):
        dst_path = f"{self.root}/{key}"
        dst_dir_path = os.path.dirname(dst_path)
        s3_url = f"s3://{self.bucket_name}/{key}"
        os.makedirs(dst_dir_path, exist_ok=True)
        if os.path.exists(dst_path) and skip_exist:
            self.logger.info(f"skip already exists in local: {s3_url}")
        else:
            self.logger.info(f"Copying: {s3_url} > {dst_path}")
            if not dryrun:
                self.bucket.download_file(key, dst_path)

    def download(self, dryrun=False, skip_exist=True):
        if self.recursive:
            objects = self.bucket.objects.filter(
                Prefix=self.prefix,
            )
            for key in [o.key for o in objects]:
                self.download_file(key, dryrun, skip_exist=skip_exist)
        else:
            self.download_file(self.prefix, dryrun, skip_exist=skip_exist)

    def upload_file(self, local_path, prefix):
        # copy local
        dst_path = f"{self.root}/{prefix}"
        self.logger.info(f"Copying to local: {local_path} => {dst_path}")
        dst_dir_path = os.path.dirname(dst_path)
        os.makedirs(dst_dir_path, exist_ok=True)
        shutil.copyfile(local_path, dst_path)

        # copy s3
        self.logger.info(
            f"Copying to s3: {local_path} => s3://{self.bucket_name}/{prefix}"
        )
        self.bucket.upload_file(local_path, prefix)

    def delete(self):
        self.logger.info(f"delete => s3://{self.bucket_name}/{self.prefix}")
        delete_path = f"{self.root}/{self.prefix}"
        self.logger.info(f"delete => {delete_path}")
        if self.recursive:
            shutil.rmtree(delete_path)
            self.bucket.objects.filter(
                Prefix=self.prefix,
            ).delete()
        else:
            os.remove(delete_path)
            self.bucket.delete_object(
                Key=self.prefix,
            )

    def upload(self, local_path, copy_root=True):
        basename = os.path.basename(local_path)
        if os.path.isfile(local_path):
            if self.prefix.endswith("/"):
                self.upload_file(local_path, f"{self.prefix}{basename}", copy_root)
            else:
                # change basename
                self.upload_file(local_path, self.prefix, copy_root)
        elif os.path.isdir(local_path):
            if self.recursive:
                files = Util.relative_files_from_dir(directory=local_path)
                for path, key in files.items():
                    self.upload_file(path, f"{self.prefix}{key}", copy_root)
            else:
                raise "not implement"
