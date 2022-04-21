Tool to train custom cellpose models via the browser on a remote server with GPU support, given cellpose training images generated using the [Train-Cellpose](http://github.com/abailoni/cellpose-training-gui) tool.

![](images/training-remotely.gif)

# How to install
Coming soon



[comment]: <> (# Installation)

[comment]: <> (- Create a conda environment with pyTorch and CUDA support)

[comment]: <> (  - This could look like `conda create --name trCellServer pytorch torchvision torchaudio cudatoolkit=11.3  -c pytorch`)

[comment]: <> (- Activate the conda environment you created in the previous step: `conda activate trCellServer` )

[comment]: <> (- `pip install -e "vcs+protocol://github.com/abailoni/cellpose-training-gui#egg=traincellposeserver&subdirectory=traincellpose-server-daemon"` )

[comment]: <> (# How to run)

[comment]: <> (- Activate env)

[comment]: <> (- `python -m traincellposeserver`)

[comment]: <> (- Optionally, you can specify a directory where to store the temporary training data:)

[comment]: <> (- `python -m traincellposeserver -d \PATH-TO-TEMP-DATA-DIR`)
