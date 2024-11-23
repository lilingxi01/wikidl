# API Reference

## Constructor: _WikiDL_

<table><thead><tr><th>Argument</th><th>Type</th><th>Description</th><th data-hidden></th></tr></thead><tbody><tr><td><code>snapshot_date</code></td><td><code>str</code></td><td>The date of the snapshot that you are trying to download. This field is required.</td><td></td></tr><tr><td><code>master_url</code></td><td><code>str</code></td><td>The master URL pointing to the data dump. By default, it is <a href="https://dumps.wikimedia.org/enwiki">https://dumps.wikimedia.org/enwiki</a></td><td></td></tr><tr><td><code>select_pattern</code></td><td><code>str</code></td><td>The file selector pattern. <code>lad</code> means the latest articles dump; <code>ehd</code> means the edit history dump. You can customize select pattern by using <code>custom_select_pattern</code> argument. By default, it is <code>lad</code>.</td><td></td></tr><tr><td><code>custom_select_pattern</code></td><td><code>str | None</code></td><td>Customize a select pattern for target file names. By default, it is <code>None</code>, so it uses specified select pattern.</td><td></td></tr><tr><td><code>num_proc</code></td><td><code>int</code></td><td>Number of processes you want to use.</td><td></td></tr><tr><td><code>log_level</code></td><td><code>int</code></td><td>The logging level that you want to use. By default, it is <code>logging.INFO</code></td><td></td></tr></tbody></table>

## Functions

### Function: _start(output\[, limit])_

This function starts downloading task that you specified in a downloader object.

<table><thead><tr><th>Argument</th><th>Type</th><th>Description</th><th data-hidden></th></tr></thead><tbody><tr><td><code>output_dir</code></td><td><code>str</code></td><td>The output directory that you want all downloaded files to go into. It is required.</td><td></td></tr><tr><td><code>limit</code></td><td><code>int | None</code></td><td>Maximum number of files to be downloaded. It is useful for debugging (you can download a few to see if it is what you want before downloading a huge batch).</td><td></td></tr></tbody></table>

