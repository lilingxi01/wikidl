import os
import shutil
from wikidl import WikiDL


download_output_dir = "./tests/download_temp"


def test_wiki_history_dump_download():
    downloader = WikiDL(
        num_proc=3,
        snapshot_date='20230401'
    )

    pending_url_batches = downloader._get_batch_urls(downloader.snapshot_date)
    assert len(pending_url_batches) > 0

    # Compute the expected filenames.
    pending_filenames = list(map(lambda url: url.split('/')[-1], pending_url_batches))

    try:
        # Start the downloader.
        downloaded_files = downloader.start(output_dir=download_output_dir, limit=4)

        assert downloader.is_started
        assert downloader.is_completed

        # Check the downloader status.
        assert len(downloaded_files) == 4

        # Check the downloaded files.
        for filepath in downloaded_files:
            filename = filepath.split('/')[-1]
            assert filename in pending_filenames
            assert os.path.exists(filepath)
    finally:
        # Clean up.
        shutil.rmtree(download_output_dir)
