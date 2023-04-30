import logging
import os
import psutil
from typing import List, Callable, Union
import shutil
from importlib.metadata import version, PackageNotFoundError
import multiprocessing as mp


def get_curr_version():
    """
    Get the version of the package.
    """
    try:
        return version('wikidl')
    except PackageNotFoundError:
        return "Package not found"


def get_file_list(input_path: str) -> List[str]:
    """
    Get the list of files in the input directory.
    :param input_path: the input directory
    :raise FileNotFoundError: if the path does not exist
    :return: the list of files
    """
    # If the path does not exist, raise an error.
    if not os.path.exists(input_path):
        raise FileNotFoundError('The path does not exist.')

    # If the input path is a file, return the list with only the file path.
    if os.path.isfile(input_path):
        return [input_path]

    # If the input path is a directory, return the list of files in the directory.
    all_files = []
    for root, directories, files in os.walk(input_path):
        for file in files:
            if file.startswith('.'):
                continue
            file_path = os.path.join(root, file)
            all_files.append(file_path)

    # Remove duplicate files. Sort them for determinism.
    all_files = sorted(list(set(all_files)))
    return all_files


def compute_total_available_space(output_dir: str) -> int:
    """
    Deprecated: Compute the total available space in the output directory.
    """
    total_available_space = shutil.disk_usage(output_dir).free

    # Display the total available space in GB.
    total_available_space_gb = total_available_space / 1024 / 1024 / 1024
    print('[Build] RDS space limitation (deprecated):', round(total_available_space_gb, 2), 'GB.')

    return total_available_space


def get_memory_consumption() -> int:
    process = psutil.Process(mp.current_process().pid)
    memory_usage_mb = process.memory_info().rss / 1024 / 1024
    return round(memory_usage_mb, 2)


def _rmtree_error_handler(func, path, exc_info):
    logging.error(f"Error occurred while calling {func.__name__} on {path}")
    logging.error(f"Error details: {exc_info}")

    # TODO: We might be able to attempt to resolve the issue based on exc_info and then retry the operation.


def cleanup_dir(path: str, onerror: Union[Callable, None] = _rmtree_error_handler):
    """
    Clean up the directory.
    :param path: the directory path
    :param onerror: the error handler
    """
    if os.path.exists(path):
        try:
            shutil.rmtree(path, onerror=onerror)
        except Exception as e:
            logging.error(f"Error occurred while removing: {path}. Check next log for details.")
            logging.error(e)


def prepare_output_dir(output_dir: str, exist_ok: bool = True):
    if os.path.exists(output_dir) and not exist_ok:
        cleanup_dir(output_dir)
    os.makedirs(output_dir, exist_ok=exist_ok)
