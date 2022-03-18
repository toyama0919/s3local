import os
import glob
from .core import Core


class Downloader(Core):
    def download_file(
        self,
        key: str,
        dryrun: bool = False,
        skip_exist: bool = True,
        dst_path: str = None,
    ):
        dst_path = dst_path or f"{self.root}/{key}"
        dst_dir_path = os.path.dirname(dst_path)
        s3_url = f"s3://{self.bucket_name}/{key}"
        os.makedirs(dst_dir_path, exist_ok=True)
        if os.path.exists(dst_path) and skip_exist:
            self.logger.info(f"skip already exists in local: {s3_url} > {dst_path}")
        else:
            self.logger.info(f"Copying: {s3_url} > {dst_path}")
            if not dryrun:
                self.bucket.download_file(key, dst_path)
        self.download_paths.append(dst_path)

    def download(
        self, dryrun: bool = False, skip_exist: bool = True, dst_path: str = None
    ):
        if self.recursive:
            objects = self.bucket.objects.filter(
                Prefix=self.prefix,
            )
            for key in [o.key for o in objects]:
                self.download_file(
                    key,
                    dryrun,
                    skip_exist=skip_exist,
                    dst_path=(
                        f"{dst_path}/{os.path.basename(key)}" if dst_path else None
                    ),
                )
        else:
            self.download_file(
                self.prefix, dryrun, skip_exist=skip_exist, dst_path=dst_path
            )

    def list_download_path(self):
        self.download()
        return self.download_paths

    def list_local_path(self, download: bool = False):
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

    def get_local_path(self, download=False):
        if download:
            self.download()
        return self.local_path
