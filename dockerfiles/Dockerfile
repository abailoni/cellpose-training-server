FROM anibali/pytorch:1.10.2-cuda11.3-ubuntu20.04

ARG TAG=latest
ARG CI_SERVER_HOST=git.embl.de
ARG CI_PROJECT_NAMESPACE=grp-alexandrov

# If run in CI of grp-alexandrov, we inherit the group's deploy tokens and can use them to clone
# repositories, download packages and images from projects within the group. For other projects, we
# might need extra tokens.
ARG CI_DEPLOY_USER
ARG CI_DEPLOY_PASSWORD

# Set up time zone.
ENV TZ=UTC
RUN sudo ln -snf /usr/share/zoneinfo/$TZ /etc/localtime

USER user

# Create a working directory
WORKDIR /app/training_data_dir

# Install cellpose and streamlit
ARG cellpose_train_dir="/tmp/cellpose-training-server"
USER $NB_USER
RUN mkdir -p "$cellpose_train_dir" && \
    git clone --filter=blob:none "https://${CI_DEPLOY_USER}:${CI_DEPLOY_PASSWORD}@${CI_SERVER_HOST}/${CI_PROJECT_NAMESPACE}/cellpose-training-server.git" "$cellpose_train_dir" && \
    conda run --name base python -m pip install --no-cache-dir --no-compile "$cellpose_train_dir" && \
    conda clean --all --force-pkgs-dirs --yes

#conda env update -n base -f /app/environment.yml \
# && rm /app/environment.yml \
# && conda clean -ya

# Trigger initial Cellpose model download to cache models and create folder with temporary training data:
RUN python -c "import cellpose.models" \
    && mkdir -p /tmp/temp_training_data

# Expose the port to be used to run the application:
EXPOSE 8501

# Create an entry point to make our image executable:
ENTRYPOINT ["traincellposeserver", "start"]
CMD ["/tmp/temp_training_data"]
