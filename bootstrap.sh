#!/bin/bash
set +e

KAIZEN_ENV=kaizen-bootstrap-env
KOMMONS_URL=https://github.com/bjoernricks/kommons/tarball/master
VIRTENV_VERSION=1.10.1
VIRTENV_TAR=virtualenv-$VIRTENV_VERSION.tar.gz
VIRTENV_URL=https://pypi.python.org/packages/source/v/virtualenv/$VIRTENV_TAR
VIRTENV_DIR=virtualenv-$VIRTENV_VERSION


if [ ! -d $VIRTENV_DIR ]; then
    # download virtualenv
    if [ ! -e $VIRTENV_TAR ]; then
        curl -O $VIRTENV_URL
    fi
    tar xvzf $VIRTENV_TAR
fi

if [ ! -d $KAIZEN_ENV ]; then
    python $VIRTENV_DIR/virtualenv.py $KAIZEN_ENV
fi

source $KAIZEN_ENV/bin/activate

# update
pip install --upgrade pip
pip install --upgrade setuptools

# install dependencies
pip install argparse
pip install sqlalchemy
pip install $KOMMONS_URL

echo ""
echo "Run source/$KAIZEN_ENV/bin/activate && ./bin/kaizen to check if all" \
    "bootstrap dependencies have been installed and kaizen can be run."
