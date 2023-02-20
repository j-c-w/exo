#!echo "Source this script!"

# set -eu

export CONDA_WORKING_DIR=/tmp/s1988171/conda_wd

if [[ ! -d /tmp/s1988171/exo ]]; then
	mkdir -p /tmp/s1988171
	# create env
	conda create --prefix /tmp/s1988171/exo python=3.9 -y
fi

eval "$(conda shell.bash hook)"
conda activate /tmp/s1988171/exo
# Get deps
pip install -r requirements.txt

# Build
python -m build
pip install dist/*.whl

# add rust deps
conda install -c conda-forge rust -y
# echo "Run: export CONDA_WORKING_DIR=/tmp/s1988171/conda_wd"
