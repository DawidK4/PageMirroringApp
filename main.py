import os 
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

urls = []
run = True

def check_url(urls):
    pass

def chech_destination(path):
    pass

def download_file(url, folder):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        filename = os.path.join(folder, os.path.basename(urlparse(url).path))
        with open(filename, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return filename
    except Exception as e:
        print(f"Failed to download {url}: {e}")

def download_page(url, folder):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html_parser")

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

while run:
    print("Menu")
    print("Please choose what do you wish to do:")
    print("1 - Mirror a website")
    print("2 - Quit")
    print("\n")

    option = input("Provide the number: ")
    if option == 1:
        user_input = input("Provide the urls (each URL has to be seperated by the comma): ")
        dir = input("Provide the absolute destination path: ")
    elif option == 2:
        run = False
    else:
        print("Please provide a valid number")
        continue