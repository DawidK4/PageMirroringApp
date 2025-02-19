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
    pass

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