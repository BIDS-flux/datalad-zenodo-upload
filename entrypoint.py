#!/usr/bin/env -S python3 -B

# NOTE: If you are using an alpine docker image
# such as pyaction-lite, the -S option above won't
# work. The above line works fine on other linux distributions
# such as debian, etc, so the above line will work fine
# if you use pyaction:4.0.0 or higher as your base docker image.

import sys
import os
import json
import datalad.api as dlad
from zenodo_client import Zenodo, Creator, Metadata, ensure_zenodo
import argparse
import shutil
import tempfile
import pathlib


def parse_args() -> dict:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="index a datalad dataset on Zenodo",
    )
    parser.add_argument(
        "--metadata-filename",
        help="file to use to set deposition metadata",
        default=".zenodo.json",
    )
    parser.add_argument(
        "--zip-name",
        help="name of the zip file to upload",
        default=os.environ["GITHUB_REF_NAME"],
    )
    parser.add_argument(
        "--recursion-limit",
        help="recursion depth of the dataset that we want to release",
    )
    parser.add_argument(
        "--zenodo_api_token",
        help="zenodo token",
        default=os.environ["ZENODO_API_TOKEN"],
    )
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help="use sandbox zenodo API",
    )
    return parser.parse_args()


def get_dataset(
    recursion_limit: int = 0,
) -> pathlib.Path:

    username_token = ""
    if "GIT_TOKEN" in os.environ:
        username_token = f"{os.environ['GIT_TOKEN']}@"
    url = f"https://{username_token}github.com/{os.environ['GITHUB_REPOSITORY']}.git"
    tmp_dir = pathlib.Path(tempfile.mkdtemp())
    ds = dlad.install(
        source=url, path=tmp_dir, recursive=True, recursion_limit=recursion_limit
    )
    return ds


def datalad_zenodo_upload(
    ds: dlad.Dataset,
    metadata_filename: str,
    zip_name: str,
    zenodo_api_token: str,
    sandbox: bool = False,
) -> (str, str):
    zip_path = os.path.join(tempfile.mkdtemp(), zip_name)
    shutil.make_archive(zip_path, "zip", ds.path)
    zip_path += ".zip"
    # zenodo = Zenodo(access_token=zenodo_api_token, sandbox=sandbox)
    metadata = Metadata.parse_file(ds.pathobj / metadata_filename)
    ensure_zenodo(
        key=os.environ["GITHUB_REPOSITORY"],
        data=metadata,
        paths=[zip_path],
        sandbox=sandbox,
    )


if __name__ == "__main__":
    args = parse_args()

    ds = get_dataset(recursion_limit=args.recursion_limit)
    datalad_zenodo_upload(
        ds, args.metadata_filename, args.zip_name, args.zenodo_api_token, sandbox=args.sandbox
    )
