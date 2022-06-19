# rapidgator-wget

Download files on RapidGator by wget.

## Usage

Please setup `config.json`:

```json
{
    "email": "your-mail@gmail.com",
    "password": "your-password",
}
```


Then, a file can be downloaded by running:

```bash
python3 rapidgator.py
```

For more options, please check:

```bash
usage: rapidgator.py [-h] [--prefix PREFIX] [--download_list DOWNLOAD_LIST]

optional arguments:
  -h, --help            show this help message and exit
  --prefix PREFIX       set download path
  --download_list DOWNLOAD_LIST
                        path to the file that stores a list of urls
```

## Limit

-   Cannot download html files.
-   Single thread download. Premium users should download from browser directly.
