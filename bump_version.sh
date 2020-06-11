#!/usr/bin/env bash

set -e

if [[ $# != 1 ]]; then
	echo "current version: $(poetry version --no-ansi | cut -d' ' -f2)"
	exit 1
fi

VERSION=$1

if [[ $(git branch --show-current) != "master" ]]; then
	echo "It's not a master branch."
	exit 1
fi

if [[ ! ${VERSION} =~ ^v([1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$ ]]; then
	echo "The version number is invalid."
	echo "E.g. v1.2.3"
	echo "current version: $(poetry version --no-ansi | cut -d' ' -f2)"
	exit 1
fi

if [[ ${VERSION} != $(poetry version --no-ansi | cut -d' ' -f2) ]]; then
	poetry version ${VERSION}

	echo "__version__ = '${VERSION}'" > ./django/config/__init__.py

	git add pyproject.toml ./django/config/__init__.py

	git commit -m "Bump version to ${VERSION}"

fi
git log -1 ${VERSION} >& /dev/null && git tag -d ${VERSION}
git ls-remote --exit-code origin ${VERSION} && git push -d origin ${VERSION}

git tag ${VERSION}
git push origin master ${VERSION}
