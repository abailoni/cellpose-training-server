# Cellpose Training Server

Tool to train custom cellpose models via the browser on a remote server with GPU support, given cellpose training images generated using the [Cellpose Annotation Tool](https://git.embl.de/grp-alexandrov/cellpose-training-gui) tool.

![](images/training-remotely.gif)

## Installation and usage on the server with GPU support

### How to build the docker image

- Clone this repository with `git clone git@git.embl.de:grp-alexandrov/cellpose-training-server.git`

- Move to the repository folder with `cd cellpose-training-server`

- To build the docker image, you will need to provide credentials to access the GitLab repository. Follow instructions [here](https://grp-alexandrov.embl-community.io/napari-spacem-qc/user-guide/access/local-installation.html#setting-up-private-package-registry) if you do not already have a `pip.config` file configured with your credentials. After that, you can use the tokens from your `pip.conf` file for the following command:

  ```
  docker build -t cellposetrainingserverapp:latest --build-arg CI_DEPLOY_USER=__your_token__ --build-arg CI_DEPLOY_PASSWORD="your_password" ./dockerfiles
  ```

### How to start the docker image 

- If you want to temporarily start the docker image, you can run the following command:

  ```shell
  docker run -p 8501:8501 --gpus all cellposetrainingserverapp:latest
  ```

- If you want to start the docker image and keep it running in the background (even when your server is restarted), you can run the following command:

  ```shell
  docker run -p 8501:8501 --gpus all --restart unless-stopped -d  cellposetrainingserverapp:latest
  ```
  
Afterwards, you can access the tool via the browser at `http://localhost:8501`
