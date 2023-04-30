import logging
import os
import re
from typing import List, Union
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup

import multiprocessing as mp

from .logger_init import _init_logger_sub_process, _init_logger_main_process, _init_logger_multiprocessing
from .utils import get_curr_version, prepare_output_dir
from .patterns import patterns


def _extract_root_url(url: str) -> str:
    parsed_url = urlsplit(url)
    root_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
    return root_url


def _avoid_duplicate_download_filenames(url_batches: List[str]):
    filenames = set()
    new_url_batches = list(set(url_batches))  # Remove duplicate URLs.
    for url in new_url_batches:
        curr_filename = url.split('/')[-1]
        if curr_filename in filenames:
            new_url_batches.remove(url)
        else:
            filenames.add(curr_filename)
    return new_url_batches


def _avoid_download_existing_files(url_batches: List[str], output_dir: str):
    new_url_batches = []
    for url in url_batches:
        target_path = os.path.join(output_dir, url.split('/')[-1])
        if not os.path.exists(target_path):
            new_url_batches.append(url)
    return new_url_batches


def _get_snapshot_dates():
    # TODO: Implement this method.
    pass


_DEFAULT_MASTER_URL = 'https://dumps.wikimedia.org/enwiki'
_DEFAULT_NUM_PROC = 1
_DEFAULT_LOG_LEVEL = logging.INFO


def url_append(url: str, unique_level: str) -> str:
    if not url.endswith('/'):
        url += '/'
    return url + unique_level


class WikiDL:
    """
    A downloader for downloading files from the web.

    Attributes:
        is_started: Whether the downloader is started.
        is_completed: Whether the downloader is completed.
    """
    def __init__(self,
                 snapshot_date: str,
                 master_url: str = _DEFAULT_MASTER_URL,
                 select_pattern: str = 'lad',
                 custom_select_pattern: Union[str, None] = None,
                 num_proc: Union[int, None] = _DEFAULT_NUM_PROC,
                 log_level: int = _DEFAULT_LOG_LEVEL):
        """
        :param snapshot_date: The date of the wiki history dump. Format: YYYYMMDD.
        :param master_url: The master URL of the wiki history dump. (default: https://dumps.wikimedia.org/enwiki/)
        :param select_pattern: The pattern to select the files to download. (default: lad)
        :param num_proc: The number of processes to use for downloading. (default: number of CPUs)
        :param log_level: The log level. (default: logging.INFO)
        """
        self.snapshot_date = snapshot_date
        self.master_url = master_url
        self.select_pattern = patterns.get(select_pattern, None) \
            if custom_select_pattern is None else custom_select_pattern
        self.num_proc = num_proc
        self.log_level = log_level

        self.is_started = False
        self.is_completed = False

        if self.select_pattern is None:
            raise ValueError(f'Select pattern not found: {select_pattern}')

        try:
            re.compile(self.select_pattern)
        except re.error:
            raise ValueError(f'Broken select pattern regex: {select_pattern}')

        _init_logger_main_process(log_level=self.log_level)

    def _worker_initializer(self, q):
        """
        Initialize the worker process.
        """
        # Initialize the logger within the sub-process.
        _init_logger_sub_process(q, log_level=self.log_level)

    def _get_batch_urls(self, date: str):
        root_url = _extract_root_url(self.master_url)
        url_batches = []
        url = url_append(self.master_url, date)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        results = soup.find_all('a', href=True)
        for f in results:
            href_link = f['href']
            if re.match(r'.*/' + self.select_pattern, href_link, re.IGNORECASE) is not None:
                url_batches.append(root_url + href_link)
        return url_batches

    def start(self, output_dir: str, limit: Union[int, None] = None):
        """
        Start the downloader.
        :param output_dir: The output directory.
        :param limit: The limit of the number of files to download. (default: None)
        """
        # Log the version.
        logging.info(f'WikiDL Version: {get_curr_version()}')

        if self.is_completed:
            raise Exception("The downloader is already completed.")
        if self.is_started:
            raise Exception("The downloader is already started.")

        # Get the batches of URLs to download.
        url_batches = self._get_batch_urls(date=self.snapshot_date)
        url_batches = _avoid_duplicate_download_filenames(url_batches=url_batches)
        url_batches = _avoid_download_existing_files(url_batches=url_batches, output_dir=output_dir)

        # Set the number of processes and limit it by the number of CPUs.
        num_proc = min(self.num_proc, os.cpu_count())

        # Mark the downloader as started.
        self.is_started = True

        # Limit the number of files to download.
        if limit is not None:
            if limit <= 0:
                logging.critical('If you want to download all files, please set limit to None or do not define it.',
                                 '0 or less than 0 are not valid limit number.')
                return
            url_batches = url_batches[:limit]

        if len(url_batches) == 0:
            logging.warning('No files are needed to download. Directly exit.')
            self.is_completed = True
            return

        # Prepare the output directory.
        prepare_output_dir(output_dir, exist_ok=True)

        # Log the number of files to download.
        logging.info(f'Will download {len(url_batches)} files.')

        # Download the files.
        logging.info(f'Start downloading. (# of assigned processes: {num_proc})')

        ql, q = _init_logger_multiprocessing(log_level=self.log_level)

        pool = mp.Pool(
            processes=num_proc,
            initializer=self._worker_initializer,
            initargs=(q,),
        )

        curr_finished = 0
        total_files = len(url_batches)
        downloaded_files = []

        # Callback function for the normal return status of a process.
        def _success_callback(downloaded_file_path):
            nonlocal downloaded_files, curr_finished
            downloaded_files.append(downloaded_file_path)
            curr_finished += 1
            curr_progress = curr_finished / total_files * 100
            logging.info(f'Progress: {curr_finished} / {total_files} = ({curr_progress:.2f}%)')

        # Callback function for the error status of a process.
        def _error_callback(e):
            nonlocal curr_finished
            curr_finished += 1
            curr_progress = curr_finished / total_files * 100
            logging.error(f'Progress: {curr_finished} / {total_files} = ({curr_progress:.2f}%) (Terminated)')

            # Log the error.
            logging.error(f'Error occurred when downloading: {e}')

        # Start processes.
        for url in url_batches:
            pool.apply_async(
                func=download_executor,
                args=(url, output_dir),
                callback=_success_callback,
                error_callback=_error_callback,
            )

        # Wait for all processes to finish.
        pool.close()
        pool.join()
        ql.stop()

        # Log the completion.
        logging.info(f'Downloading completed. {len(downloaded_files)} files are downloaded.')
        self.is_completed = True

        return downloaded_files


def download_executor(url: str, target_dir: str):
    """
    Downloads a file from the given URL to the target directory.
    This function will be used for multiprocessing.
    :param url: The URL to download.
    :param target_dir: The target directory to save the downloaded file.
    :return: The local path to the downloaded file.
    """
    # Compute the target path. Should assume that target dir exists.
    target_path = os.path.join(target_dir, url.split('/')[-1])
    # Download the file using a stream.
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(target_path, 'wb') as f:
            # Write the file in chunks of 10 MB for reduced memory usage.
            for chunk in r.iter_content(chunk_size=10 * 1024 * 1024):
                f.write(chunk)
    logging.debug(f'Downloaded done to: {target_path}.')
    return target_path
