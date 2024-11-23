---
description: >-
  WikiDL is an efficient wikipedia data dump downloader for researchers. It uses
  multiprocessing for maxing out the bandwidth and CPUs, and is friendly with
  task schedulers like Slurm.
---

# Wikimedia Dump Downloader

<figure><img src=".gitbook/assets/wikidl - cover.png" alt=""><figcaption></figcaption></figure>

## What is WikiDL?

WikiDL is a CLI downloader (also have Python version) for downloading wikipedia data dump (mainly coming from Wikimedia). The tool is designed for researchers to quickly and conveniently stay up to date with latest Wikipedia content, which is less possible to be seen by recent LLMs. It is important because a previously-seen data could drastically affect the experiment result. WikiDL just makes it as easy as possible, and lay into Slurm perfectly.

## Source of Data

In current WikiDL, the download source is [**Wikimedia Dumps**](https://dumps.wikimedia.org/enwiki/). You are able to specify the route (e.g. a mirror), but those third-party sources will not be officially supported.

WikiDL can theoretically cover all types of downloads, but currently we are focusing on downloading the latest article dump (LAD), and edit history dump (EHD).

* LAD: Latest revision of all articles existing towards the snapshot date.
* EHD: All revisions (since very beginning) of all articles existing towards the snapshot date.

## Key Features

### Slurm-friendly

The design of WikiDL is researcher-oriented. That means, we are considering use cases of researchers first. Slurm is the most common use case where WikiDL will be used, so we have made it more friendly and more easily to be used within the environment of Slurm. Such that:

* We do not use progress bar, as Slurm output shows progress bar brokenly.
* We try our best to decrease the complexity of setting up WikiDL, as we understand it is not easy to configure and change things with Slurm scheduler.
* We provide example files for you that you can just copy, paste, and run without problem.

### Resume Download

When you are trying to download a huge batch of files, we can keep track of what files are already downloaded, and do not re-download them again.

{% hint style="warning" %}
This download resume feature is file-level rather than buffer level. So currently, we do not support download resume of a huge file. That means, if the download ends in the middle of a file, then that file needs to be re-downloaded entirely.
{% endhint %}
