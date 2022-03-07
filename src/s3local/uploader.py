import os
import shutil

from .util import Util
from .core import Core


class Uploader(Core):
    def upload(self, source_path: str, skip_exist: bool = True):
        basename = os.path.basename(source_path)

        if os.path.isfile(source_path):
            if self.prefix.endswith("/"):
                key = f"{self.prefix}{basename}"
            else:
                # change basename
                key = self.prefix

            # Check if the key exists
            if skip_exist and self.exists_key(key=key):
                self.logger.info(f"skip upload {source_path} > {key}")
            else:
                self.upload_file(source_path, key)
        elif os.path.isdir(source_path):
            if self.recursive:
                objects = self.bucket.objects.filter(
                    Prefix=self.prefix,
                )
                already_upload_keys = [o.key for o in objects]
                pair = Util.relative_files_from_dir(directory=source_path)
                for abspath, relative_path in pair.items():
                    upload_key = f"{self.prefix}{relative_path}"
                    if upload_key in already_upload_keys:
                        self.logger.info(f"skip upload {upload_key}")
                    else:
                        self.upload_file(abspath, upload_key)
            else:
                raise "not implement"

    def upload_file(self, local_path: str, key: str):
        # copy local
        dst_path = os.path.join(self.root, key)
        self.logger.debug(f"Copying to local: {local_path} => {dst_path}")
        dst_dir_path = os.path.dirname(dst_path)
        os.makedirs(dst_dir_path, exist_ok=True)
        shutil.copyfile(local_path, dst_path)

        # copy s3
        self.logger.info(
            f"Copying to s3: {local_path} => s3://{self.bucket_name}/{key}"
        )
        self.bucket.upload_file(local_path, key)
