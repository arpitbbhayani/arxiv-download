arxiv-download
---

Utility to download research papers from https://arxiv.org :metal:

## Installing
**NOTE: Python3.6 is required to run this utility**

```bash
pip3 install -r requirements.txt
```

## Running
```bash
python3.6 download.py --help
```

Example
```bash
python download.py "https://arxiv.org/find/all/1/all:+Wikipedia/0/1/0/all/0/1?skip=0&query_id=a82ebfd0195719df" --output-dir ~/wikipedia-papers --all
```

> NOTE: The URL submitted should have query_id present and should look something like this https://arxiv.org/find/all/1/all:+Wikipedia/0/1/0/all/0/1?skip=0&query_id=a82ebfd0195719df

## Features
 - Downloads everything asynchronously, hence lightning fast :zap:
 - Can iterate over all pages and download all papers. Check `--all` option.
