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