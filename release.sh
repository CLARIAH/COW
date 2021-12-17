#!/bin/bash

# Releases COW to pypi via specified tag

echo 'Publishing version '$1' ...'
sleep 2
echo 'Uploading tags...'
git tag $1 -m "$1"
git push --tags origin master
sleep 2
echo 'Renaming version...'
sed -i "s/\(version\s=\s'\)[0-9]\+\.[0-9]\+\('\)/\1$1\2/" setup.py src/csvw_tool.py
sleep 2
echo 'Cleaning previous dist content...'
rm -rf dist/ local/
sleep 2
echo 'Preparing dist...'
python3 setup.py sdist
sleep 2
echo 'Uploading to pipy...'
../python3.10env/bin/twine upload dist/*
rm -rf dist/ local/
sleep 2
echo 'Upgrading user lib version...'
echo 'pip3 install cow_csvw --upgrade'
echo 'All done.'
exit 0
