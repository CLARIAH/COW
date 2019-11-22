#!/bin/bash

# Releases COW to pypi via specified tag

git tag $1 -m "$1"
git push --tags origin master
sed -i "s/x.xx/$1/" setup.py src/csvw_tool.py
rm -rf dist/
python setup.py sdist
twine upload dist/*
sudo pip install cow_csvw --upgrade
sed -i "s/$1/x.xx/" setup.py src/csvw_tool.py
