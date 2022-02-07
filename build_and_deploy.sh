
[ -z "$1" ] && echo "make sure to input [patch|minor|major]" && exit 1;
source venv/bin/activate
if [ -z "$(git status --porcelain)" ]; then
  echo "Working directory clean"
else
    git stash save -u "hold_build_deploy"
fi
bumpversion $1
python -m build
twine upload dist/*

if [ -z "$(git status --porcelain)" ]; then
  echo "Working directory clean"
else
    git stash pop
fi