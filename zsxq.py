# -*- coding: utf-8 -*-
"""
知识星球
"""
import os
import re
import time
import urllib.parse

import requests

# 忽略警告
requests.packages.urllib3.disable_warnings()
cookies = {
    'zsxq_access_token': '',
    'zsxqsessionid': '',
    'abtest_env': 'beta',
}

headers = {
    'authority': 'api.zsxq.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'origin': 'https://wx.zsxq.com',
    'referer': 'https://wx.zsxq.com/',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'x-version': '2.28.0',
}
file_headers = {
    'authority': 'api.zsxq.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'origin': 'https://wx.zsxq.com',
    'referer': 'https://wx.zsxq.com/',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
}


def text_2_mk(text: str, creat_time, images=[], files=[]):
    """
    文字转md
    """
    all_line = text.split('\n')
    title = all_line[0].replace('/', '')[:40].strip()
    if '帖子' in title and len(title) < 11:
        title += all_line[1].replace('/', '')[:40].strip()
    title += ' ' + creat_time

    # text.replace('\n', '<br>')
    w = open('article/' + title + '.md', mode='w+')
    for line in all_line:
        if title in line:
            w.writelines(f'## {line}\n')
        else:
            w.writelines(f'{line}\n')
    for image in images:
        w.write(f'![{image}]({image})\n')
    for file in files:
        w.write(f'[{file}]({file})\n')


def download(url, prefix, file_path):
    if url is None or os.path.exists(prefix + file_path):
        return file_path
    with requests.get(url, cookies=cookies, stream=True, verify=False,
                      headers={'Connection': 'close'}, timeout=(5, 10)) as r:
        if r.status_code == 200:
            chunk_size = 2048
            with open(prefix + file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
        else:
            print(url)
    return file_path


def try_get(url, params=None, **kwargs):
    try_count = 3
    error = None
    while try_count > 0:
        try:
            r = requests.get(url, params, **kwargs)
            if r.json()['succeeded']:
                return r
        except Exception as e:
            error = e
            try_count -= 1
            time.sleep(0.5)
    raise Exception(error)


def get_file_down_url(file_id):
    try:
        response = try_get(f'https://api.zsxq.com/v2/files/{file_id}/download_url', cookies=cookies,
                           headers=file_headers)
        down_url = response.json()['resp_data']['download_url']
        fn = re.findall('attname=(.*?)&', down_url)[0]
        return down_url, urllib.parse.unquote(fn)
    except:
        print(f'https://api.zsxq.com/v2/files/{file_id}/download_url')
        return None, file_id


q_params = {
    'scope': 'by_owner',
    'count': '20',
}


def get_page_title(end_time=None):
    print(end_time)
    if end_time is not None:
        q_params['end_time'] = end_time
    response = try_get('https://api.zsxq.com/v2/groups/458522225218/topics', params=q_params, cookies=cookies,
                       headers=headers)
    j = response.json()['resp_data']
    if 'topics' in j and len(j['topics']) > 1:
        for topic in j['topics']:
            talk = topic[topic['type']]
            files = []
            images = []
            if 'images' in talk:
                for img in talk['images']:
                    if 'original' in img:
                        images.append(download(img['original']['url'], 'article/', f"images/{img['image_id']}.jpg"))
                    elif 'large' in img:
                        images.append(download(img['large']['url'], 'article/', f"images/{img['image_id']}.jpg"))
                    else:
                        images.append(download(img['thumbnail']['url'], 'article/', f"images/{img['image_id']}.jpg"))
            if 'files' in talk:
                for file in talk['files']:
                    down_url, file_name = get_file_down_url(file['file_id'])
                    files.append(download(down_url, 'article/', f"files/{file_name}"))
            text_2_mk(talk['text'], topic['create_time'][:19], images, files)
            end_time = topic['create_time']
        time.sleep(1)
        get_page_title(end_time)
    print('end')


if __name__ == '__main__':
    get_page_title()
