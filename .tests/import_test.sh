#!/bin/bash
export PIP_EXTRA_INDEX_URL="https://${ART_API_USER}:${ART_API_KEY}@na.artifactory.swg-devops.com/artifactory/api/pypi/sec-iam-isam-devops-team-pypi-local/simple"
pip install -r dev-requirements.txt
#python setup.py sdist bdist_wheel
python -m build
pip install dist/ibmvia_autoconf*.whl
#export PYTHONPATH="$PYTHONPATH:$(pwd)/build/lib"

python <<EOF
import ibmvia_autoconf
assert ibmvia_autoconf.configurator != None
assert ibmvia_autoconf.appliance != None
assert ibmvia_autoconf.container != None
assert ibmvia_autoconf.webseal != None
assert ibmvia_autoconf.access_control != None
assert ibmvia_autoconf.federation != None
EOF
