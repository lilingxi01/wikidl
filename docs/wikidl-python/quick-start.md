# Quick Start

## Preparation

First, you need to make sure that WikiDL package has been installed properly. You can use any package management solution you like (e.g. `pip`, `conda`, etc.).

{% content-ref url="../installation.md" %}
[installation.md](../installation.md)
{% endcontent-ref %}

## The Simplest Example

```python
from wikidl import WikiDL

downloader = WikiDL(
    num_proc=3,
    snapshot_date='20230401'
)
downloaded_files = downloader.start(output_dir='./output')
print(downloaded_files)
```

Above code is downloading the latest articles dump (LAD) on Apr 1st, 2023, into `./output` folder. It uses 3 CPUs of your machine to download files in parallel.

{% hint style="info" %}
You can use any number of processes as you wish. However, dump provider (either Wikimedia or third-party mirror provider) may limit the number of parallel connections in order to provide fair services for everyone. You may see **503 error** if your defined number of processes exceeds the router limitation at server side.
{% endhint %}

If you are willing to see the current progress by filenames, you can add this following argument to `WikiDL` constructor:

```python
downloader = WikiDL(
    ...,
    log_level=logging.DEBUG
)
```
