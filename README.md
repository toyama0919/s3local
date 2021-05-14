# s3local

[![PyPI version](https://badge.fury.io/py/s3local.svg)](https://badge.fury.io/py/s3local)
[![Build Status](https://secure.travis-ci.org/toyama0919/s3local.png?branch=master)](http://travis-ci.org/toyama0919/s3local)

Cache the object in s3 to localhost.

Create a cache corresponding to s3 and automatically create a path for localhost and return it.

Once downloaded files remain in localhost as cache, the second migration download will be skipped

Support python3 only. (use boto3)

## Settings

aws auth support following.

* environment variables
* profile(use --aws-profile option.)
* instance profile

## Examples

#### download object and list object

```bash
$ s3local download -u s3://mybucket/artifacts/ --debug
2021-05-14 11:27:13,367 DEBUG - Copying: s3://mybucket/artifacts/main.log > /Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main.log
2021-05-14 11:27:13,367 DEBUG - Copying: s3://mybucket/artifacts/main2.log > /Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main2.log
2021-05-14 11:27:13,367 DEBUG - Copying: s3://mybucket/artifacts/main3.log > /Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main3.log
```

By default `$HOME/.s3local` is the root directory.

The format of path in local is as follows:

```
$HOME/.s3local/s3/${bucket}/${key}
```

You can change root by setting an environment variable S3LOCAL_ROOT.

```bash
$ s3local list-local -u s3://mybucket/artifacts/
/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main.log
/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main2.log
/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main3.log
```

## Python API

```python
from s3local import S3local

s3local = S3local("s3://mybucket/artifacts/")
list = s3local.list_local_path(download=True)
print(list)
#=> [
#     "/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main.log",
#     "/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main2.log",
#     "/Users/hiroshi.toyama/.s3local/s3/mybucket/artifacts/main3.log",
# ]

```

## Installation

```sh
pip install s3local
```

## CI

### install test package

```
$ ./scripts/ci.sh install
```

### test

```
$ ./scripts/ci.sh run-test
```

flake8 and black and pytest.

### release pypi

```
$ ./scripts/ci.sh release
```

git tag and pypi release.
