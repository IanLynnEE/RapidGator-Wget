import os
import argparse
import subprocess
import re
import json
from datetime import datetime

import requests


api = 'https://rapidgator.net/api/v2'
with open('config.json', 'r') as f:
    config = json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prefix', default='.', type=str,
                        help='set download path')
    parser.add_argument('--download_list', default='', type=str,
                        help='path to the file that stores a list of urls')
    args = parser.parse_args()
    path = args.prefix

    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except FileNotFoundError:
            print('Invalid prefix!')
            return

    print('Login is needed every few hours to get a valid token.', end=' ')
    if input('Login? [y/n]: ') in ['y', 'Y', 'yes', 'Yes']:
        get_token()

    if args.download_list == '':
        url = input('Input rapidgator url: ')
        download_file(url, path)
        return

    with open(args.download_list, 'r') as f:
        urls = f.readlines()
    for url in urls:
        download_file(url, path)
    return


def get_token() -> None:
    email, passwd = config['email'], config['password']
    res = requests.get(f'{api}/user/login?login={email}&password={passwd}')

    try:
        token = json.loads(res.text)['response']['token']
    except TypeError:
        print('Error! Cannot get token with response:', res)
        return

    print(f'Token successfully generated! token: {token}')
    config['token'] = token
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    return


# TODO: `name` cannot have `.html` i.e. user cannot download HTML files.
def extract_file_id_and_name(url: str) -> tuple[str, str]:
    name = None
    if '.html?referer' in url:
        file_id, name = re.search(r'file/(.*?)/(.*?).html\?', url).groups()
    elif '?referer' in url:
        file_id = re.search(r'file/(.*?)\?referer', url).group(1)
    elif '.html' in url:
        file_id, name = re.search(r'file/(.*?)/(.*?).html', url).groups()
    else:
        file_id = re.search(r'file/(.*?)(?:/)?$', url).group(1)
    return file_id, name


def download_file(url: str, path: str) -> None:
    try:
        file_id, filename = extract_file_id_and_name(url)
    except AttributeError:
        print('Error! url =', url)
        return

    url = f"{api}/file/download?file_id={file_id}&token={config['token']}"
    res = json.loads(requests.get(url).text)
    if res['status'] != 200:
        print('Error!', res)
        return
    url = res['response']['download_url']

    # If we have filename already, just download.
    if filename is not None:
        subprocess.run(['wget', '-O', os.path.join(path, filename), url])
        print('File saved:', os.path.join(path, filename))
        return

    # Otherwise, save a temp file with header in its first 10 lines.
    start_t = datetime.now().strftime('%Y%m%dT%H%M%S+08')
    tmp_name = str(os.path.join(path, start_t))
    subprocess.run(['wget', '--save-headers', '-O', tmp_name, url])

    # Now, get filename from header and remove it.
    header = subprocess.check_output(['head', '-10', tmp_name], text=True)
    if 'filename' in header:
        name = re.search(r'filename\=\"(.*?)\"', header).group(1)
        name = str(os.path.join(path, name))
        subprocess.run(['sed', '-i', '1,11d', tmp_name])
        subprocess.run(['mv', tmp_name, name])
        print('File saved:', name)
    else:
        print('Filename cannot be determined! File saved:', tmp_name)
    return


if __name__ == '__main__':
    main()
