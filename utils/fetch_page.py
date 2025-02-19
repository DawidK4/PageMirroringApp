import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

visited_urls = set()  

def download_website(url, folder):
    """Main function to start downloading the website."""
    if not os.path.exists(folder):
        os.makedirs(folder)

    crawl_page(url, folder)

def crawl_page(url, folder):
    """Crawls and downloads a webpage and its resources."""
    if url in visited_urls:
        return  

    print(f"Downloading: {url}")
    visited_urls.add(url)

    try:
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return

    parsed_url = urlparse(url)
    page_path = parsed_url.path.strip('/')
    if not page_path or page_path.endswith('/'):
        page_path += "index.html"
    if not page_path.endswith('.html'):
        page_path += ".html"

    save_path = os.path.join(folder, page_path)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    soup = BeautifulSoup(html, 'html.parser')

    update_assets(soup, url, folder)

    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

    crawl_internal_links(soup, url, folder)

def update_assets(soup, base_url, folder):
    """Finds and downloads assets like CSS, JS, and images."""
    resources = []

    for tag in soup.find_all(['link', 'script', 'img']):
        if tag.name == 'link' and tag.get('rel') == ['stylesheet']:
            resources.append(tag.get('href'))
        elif tag.name == 'script' and tag.get('src'):
            resources.append(tag.get('src'))
        elif tag.name == 'img' and tag.get('src'):
            resources.append(tag.get('src'))

    for resource in resources:
        if not resource:
            continue

        resource_url = urljoin(base_url, resource)
        parsed_url = urlparse(resource_url)
        resource_path = os.path.join(folder, parsed_url.path.lstrip('/'))

        os.makedirs(os.path.dirname(resource_path), exist_ok=True)

        try:
            res = requests.get(resource_url)
            res.raise_for_status()

            with open(resource_path, 'wb') as file:
                file.write(res.content)

            tag = soup.find(attrs={'href': resource}) or soup.find(attrs={'src': resource})
            if tag:
                if tag.name == 'link':
                    tag['href'] = os.path.relpath(resource_path, folder)
                elif tag.name in ['script', 'img']:
                    tag['src'] = os.path.relpath(resource_path, folder)

                if resource.endswith('.css'):
                    update_css_file(resource_path, base_url)
        except requests.exceptions.RequestException:
            print(f"Error downloading {resource_url}")

def update_css_file(css_path, base_url):
    """Downloads assets referenced in CSS files."""
    with open(css_path, 'r', encoding='utf-8') as file:
        css_content = file.read()

    matches = re.findall(r'url\(["\']?(.*?)["\']?\)', css_content)

    for match in matches:
        if match.startswith(('http', 'data:')):
            continue

        asset_url = urljoin(base_url, match)
        parsed_url = urlparse(asset_url)
        asset_path = os.path.join(os.path.dirname(css_path), parsed_url.path.lstrip('/'))

        os.makedirs(os.path.dirname(asset_path), exist_ok=True)

        try:
            asset_response = requests.get(asset_url)
            asset_response.raise_for_status()

            with open(asset_path, 'wb') as file:
                file.write(asset_response.content)

            css_content = css_content.replace(match, os.path.relpath(asset_path, os.path.dirname(css_path)))
        except requests.exceptions.RequestException:
            print(f"Error downloading asset: {asset_url}")

    with open(css_path, 'w', encoding='utf-8') as file:
        file.write(css_content)

def crawl_internal_links(soup, base_url, folder):
    """Finds and crawls internal links."""
    for link in soup.find_all('a', href=True):
        link_url = urljoin(base_url, link['href'])
        parsed_link = urlparse(link_url)
        parsed_base = urlparse(base_url)

        # Only follow links that belong to the same website
        if parsed_link.netloc == parsed_base.netloc:
            crawl_page(link_url, folder)
