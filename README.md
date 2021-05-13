# s3local

[![PyPI version](https://badge.fury.io/py/s3local.svg)](https://badge.fury.io/py/s3local)
[![Build Status](https://secure.travis-ci.org/toyama0919/s3local.png?branch=master)](http://travis-ci.org/toyama0919/s3local)

Command Line utility for Amazon Aurora.

Support python3 only. (use boto3)

## Settings

```sh
export AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
export AWS_DEFAULT_REGION=xx-xxxxxxx-x
```

* support environment variables and iam role.

## Examples

#### list instance and cluster

```bash
$ s3local list

[instances]
db01 mysql available db.m3.xlarge  ap-northeast-1c None
db02 mysql available db.m3.xlarge  ap-northeast-1c None
db03 mysql available db.m3.large ap-northeast-1c None
db04 mysql available db.m3.large ap-northeast-1c None
db05 aurora available db.t2.medium  ap-northeast-1c aurora-cluster
db06 aurora available db.t2.medium  ap-northeast-1c aurora-cluster

[clusters]
aurora-cluster available aurora  ['db05', 'db06']
...
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
