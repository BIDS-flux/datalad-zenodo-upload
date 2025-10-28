#!/usr/bin/env python3

# NOTE: If you are using an alpine docker image
# such as pyaction-lite, the -S option above won't
# work. The above line works fine on other linux distributions
# such as debian, etc, so the above line will work fine
# if you use pyaction:4.0.0 or higher as your base docker image.

import sys
import os
import json
import datalad.api as dlad
from datalad.config import ConfigManager
from zenodo_client import Zenodo, Creator, Metadata, ensure_zenodo
import argparse
import shutil
import tempfile
import pathlib
import logging


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
        "--archive-name",
        help="name of the zip file to upload",
        default=os.environ.get("GITHUB_REF_NAME", "release").replace(os.sep, "-"),
    )
    parser.add_argument(
        "--archive-format",
        choices=["tar", "gztar", "bztar", "xztar", "zstdtar"],
        default="gztar",
        help="archive format to upload the dataset, note that some formats might not support symlinks",
    )
    parser.add_argument(
        "--recursion-limit",
        help="recursion depth of the dataset that we want to release",
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
    logging.info("dataset installed recursively")
    return ds


def datalad_zenodo_upload(
    ds: dlad.Dataset,
    metadata_filename: str,
    archive_name: str,
    archive_format: str,
#    zenodo_api_token: str,
    sandbox: bool = False,
) -> (str, str, str):
    with tempfile.TemporaryDirectory() as tmp_dir:
        archive_bname = os.path.join(tmp_dir, archive_name)
        archive_path = shutil.make_archive(archive_bname, archive_format, ds.path)
        logging.info("archive created")
        metadata = Metadata.parse_file(ds.pathobj / metadata_filename)
        res = ensure_zenodo(
            key=os.environ["GITHUB_REPOSITORY"],
            data=metadata,
            paths=[archive_path],
            sandbox=sandbox,
        )
        res_json = res.json()
        logging.info("uploaded to zenodo")
    return res_json["doi"], res_json["doi_url"], res_json['files'][0]['links']['download']


def setup_git(
        username=os.environ.get('GIT_USERNAME'),
        email=os.environ.get('GIT_EMAIL'),
    ):

    config = ConfigManager()
    if username and email:
        config.set('user.name', username, scope='global')
        config.set('user.email', email, scope='global')

if __name__ == "__main__":
    args = parse_args()
    setup_git()
    ds = get_dataset(recursion_limit=args.recursion_limit)
    doi, zenodo_url, archive_url = datalad_zenodo_upload(
        ds,
        args.metadata_filename,
        args.archive_name,
        sandbox=args.sandbox,
        archive_format=args.archive_format,
    )
    if "GITHUB_OUTPUT" in os.environ :
        with open(os.environ["GITHUB_OUTPUT"], "a") as f :
            print("{0}={1}".format("doi", doi), file=f)
            print("{0}={1}".format("zenodo_url", zenodo_url), file=f)
            print("{0}={1}".format("archive_url", archive_url), file=f)
