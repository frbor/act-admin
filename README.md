# ACT Admin

## Introduction

This package should only be used with act-api, act-workers, act-types at version 2.x.x.

This package contains management utilities for the [ACT Platform](https://github.com/mnemonic-no/act-platform).

## Installation
1. This project requires that you have a running installation of the [act-platform](https://github.com/mnemonic-no/act-platform).
2. Install from pip
```bash
pip install act-admin
```

## act-origin [usage](usage)

```bash
$ act-origin --act-baseurl <BASEURL> --user-id <USERID> --add
Origin name: myorigin
Origin description: My Test Origin
Origin trust (float 0.0-1.0. Default=0.8):
Origin organization (UUID):
[2019-11-11 10:46:22] app=origin-client level=INFO msg=Created origin: myorigin
Origin added:
Origin(name='myorigin', id='e5a9792e-78c7-4190-9275-27616be47ca8', organization=Organization(), description='My Test Origin', trust=0.8)
```

## act-types usage
To bootstrap the type system with default types (userid/act-baseurl must point to ACT installation):
```
act-types \
    --user-id 1 \
    --act-baseurl http://localhost:8888 \
    --loglevel ERROR \
    --default-object-types \
    --default-fact-types \
    --default-meta-fact-types \
    --add
```

It is safe to rerun the command above, after new types have been added to the data model.

You can also add types from your own files, using --object-types-file, --fact-types-file and --meta-fact-types-file that points to a json file on the same format as the [default types](https://github.com/mnemonic-no/act-types/tree/master/act/types/etc).

To show default types (replace with fact/meta-fact for other types):
```bash
act-types --default-object-types list
```

# Local development

Use pip to install in [local development mode](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs). act-types (and act-api) uses namespacing, so it is not compatible with using `setup.py install` or `setup.py develop`.

In repository, run:

```bash
pip3 install --user -e .
```

It is also necessary to install in local development mode to correctly resolve the files that are read by the `--default-*` options when doing local changes. These are read from etc under act.types and if the package is installed with "pip install act-types" it will always read the files from the installed package, even though you do changes in a local checked out repository.
