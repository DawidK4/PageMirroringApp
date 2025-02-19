import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def check_url(urls):
    valid_urls = []
    for url in urls:
        url = url.strip()
        try:
            response = requests.head(url)
            if response.status_code < 400:
                valid_urls.append(url)
            else:
                print(f"Skipping {url}: Invalid response code {response.status_code}")
        except requests.RequestException as e:
            print(f"Skipping {url}: {e}")
    return valid_urls

def check_destination(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download_file(url, folder):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        filename = os.path.join(folder, os.path.basename(urlparse(url).path) or "index.html")
        with open(filename, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return filename
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def download_page(url, folder):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all(["img", "link", "script"]):
            attr = "src" if tag.name in ["img", "script"] else "href"
            if tag.has_attr(attr):
                asset_url = urljoin(url, tag[attr])
                asset_filename = download_file(asset_url, folder)
                if asset_filename:
                    tag[attr] = os.path.basename(asset_filename)

        page_filename = os.path.join(folder, "index.html")
        with open(page_filename, "w", encoding="utf-8") as file:
            file.write(str(soup))

        print(f"Downloaded: {url}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

while True:
    print("\nMenu")
    print("1 - Mirror a website")
    print("2 - Quit")

    option = input("Provide the number: ").strip()
    
    if option == "1":
        user_input = input("Provide the URLs (separated by commas): ")
        dir_path = input("Provide the absolute destination path: ").strip()
        
        urls = user_input.split(",")
        urls = check_url(urls)
        
        if not urls:
            print("No valid URLs provided. Exiting...")
            continue
        
        check_destination(dir_path)

        for url in urls:
            print(f"Processing {url}...")
            folder = os.path.join(dir_path, urlparse(url).netloc)
            check_destination(folder)
            download_page(url, folder)

        print("Mirroring completed.")

    elif option == "2":
        print("Exiting...")
        break
    else:
        print("Please provide a valid number.")
