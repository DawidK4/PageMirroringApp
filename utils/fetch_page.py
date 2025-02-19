import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def download_website(url, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

    response = requests.get(url)
    html = response.text

    html_filename = os.path.join(folder, 'index.html')
    with open(html_filename, 'w', encoding='utf-8') as file:
        file.write(html)

    soup = BeautifulSoup(html, 'html.parser')
    resources = []

    for tag in soup.find_all(['link', 'script', 'img']):
        if tag.name == 'link' and tag.get('rel') == ['stylesheet']:
            resources.append(tag.get('href'))
        elif tag.name == 'script' and tag.get('src'):
            resources.append(tag.get('src'))
        elif tag.name == 'img' and tag.get('src'):
            resources.append(tag.get('src'))

    for resource in resources:
        resource_url = urljoin(url, resource)
        parsed_url = urlparse(resource_url)
        resource_path = os.path.join(folder, parsed_url.path.lstrip('/'))

        os.makedirs(os.path.dirname(resource_path), exist_ok=True)

        try:
            resource_response = requests.get(resource_url)
            with open(resource_path, 'wb') as file:
                file.write(resource_response.content)

            tag = soup.find(attrs={'href': resource}) or soup.find(attrs={'src': resource})
            if tag:
                if tag.name == 'link':
                    tag['href'] = os.path.relpath(resource_path, folder)
                elif tag.name == 'script' or tag.name == 'img':
                    tag['src'] = os.path.relpath(resource_path, folder)

                if resource.endswith('.css'):
                    update_css_file(resource_path, url)
        except requests.exceptions.RequestException:
            print(f"Error downloading {resource_url}")

    with open(html_filename, 'w', encoding='utf-8') as file:
        file.write(str(soup))

def update_css_file(css_path, base_url):
    with open(css_path, 'r', encoding='utf-8') as file:
        css_content = file.read()

    matches = re.findall(r'url\(["\']?(.*?)["\']?\)', css_content)

    for match in matches:
        if not match.startswith(('http', 'data:')):
            asset_url = urljoin(base_url, match)
            parsed_url = urlparse(asset_url)
            asset_path = os.path.join(os.path.dirname(css_path), parsed_url.path.lstrip('/'))

            os.makedirs(os.path.dirname(asset_path), exist_ok=True)

            try:
                asset_response = requests.get(asset_url)
                with open(asset_path, 'wb') as file:
                    file.write(asset_response.content)

                css_content = css_content.replace(match, os.path.relpath(asset_path, os.path.dirname(css_path)))
            except requests.exceptions.RequestException:
                print(f"Error downloading asset: {asset_url}")

    with open(css_path, 'w', encoding='utf-8') as file:
        file.write(css_content)
