#!/bin/bash
set -e
# https://packaging.python.org/en/latest/tutorials/packaging-projects/
[ -z "$1" ] && echo "make sure to input [patch|minor|major]" && exit 1;
source .venv/bin/activate

bumpversion $1 --no-tag
uv lock

# commit lock file
git add pyproject.toml
git add uv.lock

VERSION=$(python -c 'import proflow.version as v; print(v.version)')
git commit -m "Update lock file"
echo "Updated to version $VERSION"

# create tag for new version
git tag "v$VERSION"

# push tags
git push
git push --tags
