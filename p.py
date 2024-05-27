#!/usr/bin/env python3
import os
import re
import json
import requests
from bs4 import BeautifulSoup
from packaging import version

import logging
logging.basicConfig(filename='utils/log.log', level=logging.INFO)

def req(url, output=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android 13; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    if output:
        with open(output, 'wb') as f:
            f.write(response.content)

    return response.content

def filter_lines(pattern, buffer):
    result_buffer = []
    last_target_index = -1
    collecting = False
    temp_buffer = []

    for index, line in enumerate(buffer):
        if re.search(r'<a\s+class="accent_color"', line):
            last_target_index = index
            collecting = True
            temp_buffer = []

        if collecting:
            temp_buffer.append(line)

        if re.search(pattern, line):
            if last_target_index != -1 and collecting:
                result_buffer.extend(temp_buffer)
                collecting = False

    return result_buffer

def get_supported_version(pkg_name):
    filename = 'patches.json'

    with open(filename, 'r') as f:
        data = json.load(f)

    versions = set()

    for patch in data:
        compatible_packages = patch.get('compatiblePackages', [])

        for package in compatible_packages:
            if package.get('name') == pkg_name and package.get('versions'):
                versions.update(package['versions'])

    return max(versions, key=version.parse) if versions else None

def apkmirror(org, name, package, arch=None, dpi=None):
    dpi = dpi or 'nodpi'
    version = os.environ.get('VERSION')

    if not version:
        supported_version = get_supported_version(package)

        if supported_version:
            version = supported_version
            os.environ['VERSION'] = version
        else:
            page = f'https://www.apkmirror.com/uploads/?appcategory={name}'
            page_content = req(page)

            soup = BeautifulSoup(page_content, 'html.parser')
            versions = [link.text for link in soup.find_all(class_='fontBlack') if 'alpha' not in link.text.lower() and 'beta' not in link.text.lower()][:20]

            versions = sorted(versions, key=version.parse, reverse=True)
            version = versions[0]
            os.environ['VERSION'] = version

    url = f'https://www.apkmirror.com/apk/{org}/{name}/{name}-{version}-release'
    apk_page_content = req(url)

    lines = apk_page_content.decode('utf-8').split('\n')

    if dpi:
        lines = filter_lines(f'>\s*{dpi}\s*<', lines)
    if arch:
        lines = filter_lines(f'>\s*{arch}\s*<', lines)
    lines = filter_lines('>\\s*APK\\s*<', lines)

    download_page_url = None
    for line in lines:
        match = re.match(r'.*href="(.*[^"]*\/)"', line)
        if match:
            download_page_url = match.group(1)
            if not download_page_url.startswith('https://www.apkmirror.com'):
                download_page_url = f'https://www.apkmirror.com{download_page_url}'
            break

    download_page_content = req(download_page_url)
    lines = download_page_content.decode('utf-8').split('\n')

    dl_apk_url = None
    for line in lines:
        match = re.search(r'href="(.*key=[^"]*)"', line)
        if match:
            dl_apk_url = match.group(1)
            if not dl_apk_url.startswith('https://www.apkmirror.com'):
                dl_apk_url = f'https://www.apkmirror.com{dl_apk_url}'
            break

    dl_apk_content = req(dl_apk_url)
    lines = dl_apk_content.decode('utf-8').split('\n')

    final_url = None
    for line in lines:
        match = re.search(r'href="(.*key=[^"]*)"', line)
        if match:
            final_url = match.group(1)
            if not final_url.startswith('https://www.apkmirror.com'):
                final_url = f'https://www.apkmirror.com{final_url}'
            final_url = final_url.replace('amp;', '')
            if not final_url.endswith('&forcebaseapk=true'):
                final_url += '&forcebaseapk=true'
            break

    apk_filename = f'{name}-v{version}.apk'
    req(final_url, apk_filename)

if __name__ == "__main__":
    apkmirror("org", "name", "package")
