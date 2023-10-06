import re
from typing import NewType
import requests
from bs4 import BeautifulSoup

bio_entity = NewType('bio_entity', str)
ec_number = NewType('ec_number', str)


def get_protein_links(identifier: str) -> list[bio_entity]:

    website = "https://go.drugbank.com"
    url = f"{website}/unearth/q?searcher=bio_entities&query={identifier}"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    cards = soup.select(".unearth-search-hit ")

    protein_matches: list[bio_entity] = []

    for card in cards:
        text_area = card.select(".text-muted")[0]
        ec_codes = text_area.find_all("em")
        for ec_code in ec_codes:
            if ec_code.text == identifier:
                protein_selector = card.select(".hit-link")[0]
                bio_id = protein_selector.select(
                    "a[href]")[0].attrs.get("href")
                if bio_id and bio_id not in protein_matches:
                    protein_matches.append(bio_entity(bio_id))

    return protein_matches


def get_links_list(identifier: str | list):

    match identifier:
        case str():
            setOfLinks = get_protein_links(identifier)
        case list():
            setOfLinks = []
            for id in identifier:
                setOfLinks.extend(get_protein_links(id))
        case _:
            raise Exception("Identifier must be a string or a list of strings")

    if setOfLinks:
        with open("files/EClinks.txt", "a") as f:
            f.write(f">{identifier}\n")
            for i in setOfLinks:
                f.write(f"{i}\n")
    else:
        with open("files/emptyEC.txt", "a") as f:
            f.write(f">{identifier}\n")
            for i in setOfLinks:
                f.write(f"{i}\n")


def get_bio_id_links(filename) -> None:
    ec_numbers: list[ec_number | list[ec_number]] = []
    with open(filename, "r") as f:
        for line in f.readlines():
            line_to_process = line.strip()
            match line_to_process[0]:
                case '[':
                    parts = re.findall("([1-9][1-9.-]*)", line_to_process)
                    line_to_process = list(
                        map(lambda ec: ec_number(ec), parts))
                    ec_numbers.append(line_to_process)
                case _:
                    ec_numbers.append(ec_number(line_to_process))

    for idx, ec in enumerate(ec_numbers):
        get_links_list(ec)
        print(f"{idx+1}/{len(ec_numbers)}")


def read_ecs():
    ec_dict = {}
    ec = []
    ec_name = ""

    with open("files/EClinks.txt", "r") as f:
        for line in f.readlines():
            if line.strip()[0] != ">":
                ec.append(line.strip())
            else:
                ec_dict[ec_name] = ec
                ec_name = line.strip()[1:]
                ec = []
    return ec_dict


if __name__ == "__main__":
    get_protein_links("1.4.3.4")
