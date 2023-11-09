#!/bin/bash

# Releases COW to pypi via specified tag

CURRENT_TAG=$(git tag | tail -n1)

# test if we have access to twine
if [ -z "$TWINE_PATH" ];
then
    TWINE_PATH=$(command -v twine)
	if [ $? -eq 0 ];
    then
        # found a system binary
        break
    elif [ ! $(python3 -m twine &> /dev/null ; echo $?) ];
	then
        # found a Python module
		TWINE_PATH="python3 -m twine"
	else
		# check for virtual environment on current and higher level
		TWINE_PATH=$(find ../ -type f -name twine)
		if [ $(echo "$TWINE_PATH" | wc -l) -ne 1 ];
		then
			echo "Cannot find Python module 'twine'."
			echo "Please install twine or run this script with 'env TWINE_PATH=...' to specify its location."

			exit 2
		fi
	fi
fi

function do_update () {
	echo ' - uploading tags'
	git tag "$1" -m "Release of COW $1"
	git push --tags origin base

	sleep 1

	echo ' - updating documentation'
	sed -i "s/\(version\s=\s'\)[0-9]\+\.[0-9]\+\('\)/\1$1\2/" setup.py src/csvw_tool.py
	
	sleep 1

	echo ' - cleaning outdated cache'
	rm -rf dist/ local/

	sleep 1

	echo ' - preparing new distibution'
	python3 setup.py sdist

	sleep 1
	
    echo ' - uploading update to PiPy (using $TWINE_PATH)'
	"$TWINE_PATH" upload dist/*

	sleep 1

	echo ' - cleaning cache'
	rm -rf dist/ local/
}

echo "============================================"
echo " CSV On the Web (COW) - Release update tool "
echo "============================================"
echo "current tag: $CURRENT_TAG"
echo -n "new tag: "
read NEW_TAG
echo -n "Release update under tag: $NEW_TAG ? ( Y / [N] ) "
read UPDATE

case "$UPDATE" in
	y|Y|yes|Yes)
		do_update "$NEW_TAG"
		;;
	*)
		exit 1
		;;
esac

exit 0
