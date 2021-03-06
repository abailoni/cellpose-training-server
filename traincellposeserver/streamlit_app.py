import argparse
import pathlib
import time
import zipfile
import random
import streamlit as st

import os
import shutil
import subprocess
import sys
from os import listdir

import yaml

try:
    import cellpose
except ImportError:
    cellpose = None


from streamlit.report_thread import REPORT_CONTEXT_ATTR_NAME
from threading import current_thread
from contextlib import contextmanager
from io import StringIO

@contextmanager
def st_redirect(src, dst):
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)

    with StringIO() as buffer:
        old_write = src.write

        def new_write(b):
            if getattr(current_thread(), REPORT_CONTEXT_ATTR_NAME, None):
                buffer.write(b + '')
                output_func(buffer.getvalue() + '')
            else:
                old_write(b)

        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write


@contextmanager
def st_stdout(dst):
    "this will show the prints"
    with st_redirect(sys.stdout, dst):
        yield


@contextmanager
def st_stderr(dst):
    "This will show the logging"
    with st_redirect(sys.stderr, dst):
        yield


def start_cellpose_training(training_folder):
    try:
        import cellpose
    except ImportError:
        return False, "cellpose module is required to train a custom model"

    # Assert that training data is present:
    training_images_dir = os.path.join(training_folder, "training_images")
    training_config_path = os.path.join(training_folder, "train_config.yml")
    if not os.path.exists(training_folder):
        return False, "Temp training data folder not found, something went wrong: {}".format(training_folder)
    if not os.path.exists(training_images_dir):
        return False, "Folder named `training_images` not found in zip file"
    if not os.path.exists(training_config_path):
        return False, "Training config `train_config.yml` not found in zip file"

    # Load config:
    with open(training_config_path, 'r') as f:
        training_config = yaml.load(f, Loader=yaml.FullLoader)

    training_was_successful, message = \
        _run_training(training_images_dir,
                      *training_config.get("cellpose_args", []),
                      **training_config.get("cellpose_kwargs", {}))

    return training_was_successful, message


def _run_training(train_folder,
                  *cellpose_args,
                  test_folder=None,
                  out_models_folder=None,
                  **cellpose_kwargs
                  ):
    """
    :param cellpose_args: List of strings that should be passed to cellpose (those arguments that do not require a specific value)
    """
    if cellpose is None:
        return False, "cellpose module is required to train a custom model"

    # Compose the command to be run:
    # TODO: move fast_mode to config?
    # TODO: convert command to list of elements and disable the option shell=True
    python_interpreter = sys.executable
    CUDA_VISIBLE_DEVICES = os.environ["CUDA_VISIBLE_DEVICES"] if "CUDA_VISIBLE_DEVICES" in os.environ else "0"
    command = "{} {} -m cellpose {} --train" \
              " --use_gpu --fast_mode --dir {} {} ".format(
        "CUDA_VISIBLE_DEVICES=" + CUDA_VISIBLE_DEVICES,
        python_interpreter,
        "--" if "ipython" in python_interpreter else "",
        train_folder,
        "" if test_folder is None else "--test_dir {}".format(test_folder),
    )
    # Add the args:
    for arg in cellpose_args:
        assert isinstance(arg, str), "Arguments should be strings"
        command += "--{} ".format(arg)

    # Add the kwargs:
    for kwarg in cellpose_kwargs:
        command += "--{} {} ".format(kwarg, cellpose_kwargs[kwarg])

    # print(command)
    fake_command = "ls"
    output = subprocess.run(fake_command, shell=True, capture_output=True, text=True)
    if output.returncode != 0:
        return False, output.stderr

    # process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE)
    with st_stdout("code"), st_stderr("code"):
        print(command)
        with subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
            for line in process.stdout:
                print(line)
                # logging.warning(line)
            # print(line)
    # for c in iter(lambda: process.stdout.read(1), b""):
    #     sys.stdout.buffer.write(c)
    #     logging.warning(f'Counting... 3')
        # f.buffer.write(c)

    if out_models_folder is not None:
        os.makedirs(out_models_folder, exist_ok=True)
        basedir, dirname = os.path.split(out_models_folder)
        if dirname != "models":
            out_models_folder = os.path.join(out_models_folder, "models")

        # Copy new trained models to target folder:
        cellpose_out_model_dir = os.path.join(train_folder, "models")
        shutil.copytree(cellpose_out_model_dir, out_models_folder, dirs_exist_ok=True)

        # Now delete the original folder:
        shutil.rmtree(cellpose_out_model_dir)

    return True, output.stdout


@st.cache(suppress_st_warning=True)
def process_zip(file_object, train_dir):
    if file_object is not None:
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            zip_ref.extractall(train_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--temp_data_dir', required=False,
                        default=os.path.join(os.getcwd(), "_training_data"), type=str,
                        help='Directory where to store temporary training files')

    args = parser.parse_args()
    data_dir = args.temp_data_dir
    os.makedirs(data_dir, exist_ok=True)


    # logging.warning(f'Counting... 3')
    uploaded_file = st.file_uploader("Upload cellpose training data", type="zip")
    if uploaded_file is not None:
        # Display bar:
        # my_bar = st.progress(0)

        # Button for starting training:
        btn = st.button("Start training")
        if btn:
            model_name, _ = os.path.splitext(uploaded_file.name)
            training_id = random.randint(0, 10000)
            training_dir = os.path.join(data_dir, "training_data_{}_{}".format(model_name, training_id))
            training_dir = os.path.abspath(training_dir)

            # Unzip data:
            os.makedirs(training_dir, exist_ok=True)
            process_zip(uploaded_file, train_dir=training_dir)
            assert os.path.exists(training_dir), "Check1"

            # Display some messages:
            # st.info("Training data is being processed")
            # my_bar.progress(10)

            # Start training:
            # st.info(model_name)

            sub_folders = listdir(training_dir)
            if "training_images" not in sub_folders:
                training_path = os.path.join(training_dir, model_name)
            # training_path = os.path.join(training_dir, model_name)
            else:
                training_path = training_dir
            assert os.path.exists(training_path), "Check2"
            tick = time.time()
            with st.spinner('Training has started...'):
                training_was_successful, output_message = start_cellpose_training(training_path)
            training_runtime = time.time() - tick

            if not training_was_successful:
                # st.error("Training could not be completed")
                st.error("Training could not be completed. See error message below:")
                st.write(output_message)
            else:
                # my_bar.progress(90)
                models_dir = os.path.join(training_path, "training_images", "models")
                out_zip_file = os.path.join(training_path, "{}_trained_models.zip".format(model_name))

                with zipfile.ZipFile(out_zip_file, mode="w") as archive:
                    for file_path in pathlib.Path(models_dir).iterdir():
                        archive.write(file_path, arcname=file_path.name)

                with st.sidebar:
                    st.success("Training was completed successfully in {:.2f} s. You can now download "
                               "the trained cellpose model:".format(training_runtime))
                    # with st.sidebar:
                    with open(out_zip_file, "rb") as fp:
                        btn = st.download_button(
                            label="Download the trained models (zip)",
                            data=fp,
                            file_name=os.path.split(out_zip_file)[1],
                            mime="application/zip"
                        )

                # my_bar.progress(100)
                # st.download_button('Download training log', output_message)

        else:
            # st.write("Deleting old training data")
            pass
            # Clean any temporary training data that was stored on disk:
            shutil.rmtree(data_dir)

