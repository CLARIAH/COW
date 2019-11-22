#!/bin/bash

# Releases COW to pypi via specified tag

echo 'Publishing version '$1' ...'
sleep 2
echo 'Uploading tags...'
git tag $1 -m "$1"
git push --tags origin master
sleep 2
echo 'Renaming version...'
sed -i "s/x.xx/$1/" setup.py src/csvw_tool.py
sleep 2
echo 'Cleaning previous dist content...'
rm -rf dist/ local/
sleep 2
echo 'Preparing dist...'
python setup.py sdist
sleep 2
echo 'Uploading to pipy...'
twine upload dist/*
rm -rf dist/ local/
sleep 2
echo 'Renaming back to version generic...'
sed -i "s/$1/x.xx/" setup.py src/csvw_tool.py
echo 'Upgrading user lib version...'
sleep 10
pip install cow_csvw --upgrade
echo 'All done.'
exit 0
