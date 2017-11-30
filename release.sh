#!/bin/bash

# Releases COW to pypi via specified tag

git tag $1 -m "$1"
git push --tags origin master
sed -i "s/x.xx/$1/" setup.py
python setup.py sdist upload -r pypi 
sudo pip install cow_csvw --upgrade
