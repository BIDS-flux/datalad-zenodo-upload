# datalad-zenodo-upload

A GitHub Action that publishes a [DataLad](https://www.datalad.org) dataset to [Zenodo](https://zenodo.org), including sub-datasets and the full git history.

The action clones the repository it runs in with `datalad install`, optionally fetches sub-datasets recursively, archives the result (with its `.git`), and uploads the archive to Zenodo using the deposition metadata stored in the dataset. Once the archive is extracted, it is a regular DataLad dataset and can be used directly (`datalad get`, etc.).

## Requirements

1. **A Zenodo access token** with the `deposit:write` and `deposit:actions` scopes, stored as a repository secret (e.g. `ZENODO_TOKEN`). Create one at <https://zenodo.org/account/settings/applications/> (or <https://sandbox.zenodo.org/...> for the sandbox).
2. **A `.zenodo.json` file at the root of the dataset** describing the deposition. It is validated as a `zenodo_client` `Metadata` object (the same format Zenodo's GitHub integration uses). Minimal example:

   ```json
   {
     "upload_type": "dataset",
     "title": "My dataset",
     "creators": [{"name": "Doe, Jane", "affiliation": "Some University"}],
     "description": "What this dataset contains",
     "access_right": "open",
     "license": "cc-by-4.0",
     "keywords": ["datalad"]
   }
   ```
3. The repository must be accessible via `https://github.com/<owner>/<repo>.git` without credentials (public repo). Sub-dataset content is not downloaded (`get_data=False`), only the dataset structure and git history.

## Usage

Typically run when a release is published:

```yaml
name: Release to Zenodo
on:
  release:
    types: [published]

jobs:
  zenodo:
    runs-on: ubuntu-latest
    steps:
      - name: Upload to Zenodo
        id: zenodo
        uses: BIDS-flux/datalad-zenodo-upload@main   # pin to a release tag in practice
        with:
          zenodo_token: ${{ secrets.ZENODO_TOKEN }}
          recursion_limit: 1
          archive_format: gztar
          sandbox: false

      - name: Show result
        run: |
          echo "DOI: ${{ steps.zenodo.outputs.doi }}"
          echo "Record: ${{ steps.zenodo.outputs.zenodo_url }}"
          echo "Archive: ${{ steps.zenodo.outputs.archive_url }}"
```

No `actions/checkout` step is needed: the action clones the repository itself.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `zenodo_token` | yes | – | Zenodo API token used to authenticate. |
| `recursion_limit` | no | `0` | Depth of sub-datasets to install recursively (`0` = only the top-level dataset). |
| `additional_subdatasets` | no | – | Space-separated list of sub-dataset paths to include even if they are beyond `recursion_limit`. |
| `archive_format` | no | `gztar` | Archive format, as accepted by [`shutil.make_archive`](https://docs.python.org/3/library/shutil.html#shutil.make_archive): `tar`, `gztar`, `bztar`, `xztar`, `zstdtar`. Some formats may not preserve symlinks. |
| `sandbox` | no | `false` | Set to `true` to upload to the [Zenodo sandbox](https://sandbox.zenodo.org) instead of production. Use it to test your setup first. |

## Outputs

| Output | Description |
|--------|-------------|
| `doi` | DOI of the created Zenodo record. |
| `zenodo_url` | URL of the Zenodo record (DOI URL). |
| `archive_url` | Download URL of the uploaded archive. |

## Archive layout

The archive is named `<repo-name>-<ref-name>.<ext>` (e.g. `my-dataset-v1.0.tar.gz`) and contains a single top-level directory of the same name, so extracting it yields a clean `my-dataset-v1.0/` dataset directory.

## Development

The action runs as a Docker container (see `Dockerfile`, `entrypoint.py`). Unit tests:

```sh
pip install -r requirements.txt
python3 -m unittest tests/tests.py
```

## License

See [LICENSE](LICENSE).
