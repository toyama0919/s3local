from pathlib import Path
import os
from glob import glob
from urllib.parse import urlparse


class Util:
    @staticmethod
    def relative_files_from_dir(directory: str):
        abspath = os.path.abspath(directory)
        parent = Path(abspath).parent
        glob_string = f"{abspath}/**/*"
        paths = glob(glob_string, recursive=True)

        results = {}
        for path in paths:
            if os.path.isfile(path):
                results[path] = path.lstrip(str(parent))
        return results

    @staticmethod
    def get_bucket_and_prefix_from_url(url):
        o = urlparse(url)
        return o.scheme, o.netloc, o.path.lstrip("/")
