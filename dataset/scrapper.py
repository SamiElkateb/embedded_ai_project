import requests
import re
import os
from time import sleep
from bs4 import BeautifulSoup

URL_REGEX = re.compile("https://xeno-canto.org/([0-9]+)/download")

species_list = [
     { 
        "name": "alauda arvensis", 
        "page": 1
     },
     { 
        "name": "emberiza citrinella", 
        "page": 1
     },
     { 
        "name": "sylvia borin", 
        "page": 1
     },
     { 
        "name": "delichon urbicum", 
        "page": 1
     },
     { 
        "name": "cuculus canorus", 
        "page": 1
     },
     { 
        "name": "muscicapa striata", 
        "page": 1
     },
     { 
        "name": "tachybaptus ruficollis", 
        "page": 1
     },
     { 
        "name": "emberiza cirlus", 
        "page": 1
     },
     { 
        "name": "tyto alba", 
        "page": 1
     },
     { 
        "name": "falco tinnunculus", 
        "page": 1
     },
]
    
def get_links(species: str, page: int):
    species = species.replace(" ", "+")
    has_more_pages = False
    res = requests.get(f"https://xeno-canto.org/explore?query={species}+type:song+q:A+&pg={str(page)}")
    soup = BeautifulSoup(res.text, 'html.parser')
    links = soup.find("result")
    results_table = soup.select('tr>td>a')
    links = []
    for link in results_table:
        if 'download' in link['href']:
            links.append(link['href'])

    results_table = soup.select('a')
    for link in results_table:
        if 'pg=' in link['href']:
            page_nb = (re.findall("pg=([0-9]+)", str(link['href'])))[0]
            page_nb = int(page_nb)
            if page_nb > page:
                has_more_pages = True
    return links, has_more_pages

def download_links(links: list[str], species: str):
    species = species.replace(" ", "_")
    relative_path = f'./{species}/downloaded.txt'
    absolute_path = os.path.dirname(__file__)
    full_path = os.path.join(absolute_path, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(f'./{species}/downloaded.txt',"a") as file:
        file.write('start_page\n')
        for link in links:
            file.write(f'downloaded: {link}\n') 
            try:
                res = requests.get(link, allow_redirects=True)
                content_disposition = res.headers['Content-Disposition'].replace(" ", "-")
                filename = (re.findall("filename=(\S+)", content_disposition))[0].replace("\"", "")
                relative_path = f'./{species}/{filename}'
                absolute_path = os.path.dirname(__file__)
                full_path = os.path.join(absolute_path, relative_path)
                open(full_path, 'wb').write(res.content)
                sleep(2)
            except:
                file.write(f'error: {link}\n') 
        file.write('end_page\n')


if __name__ == '__main__':
    for species in species_list:
        has_more_pages = True
        page=species["page"]
        with open('downloaded.txt',"a") as file:
            file.write(f'{"="*10}{species}{"="*10}\n')
        try:
            while(has_more_pages):
                try: 
                    links, has_more_pages = get_links(species["name"], page)
                    download_links(links, species["name"])
                    with open('downloaded.txt',"a") as file:
                        file.write(f'{page}\n')
                except: 
                    with open('downloaded.txt',"a") as file:
                        file.write(f'error: {page}\n')
                page +=1
                if page > 5:
                    has_more_pages = False
        except:
            print(f'error {species}')
            

