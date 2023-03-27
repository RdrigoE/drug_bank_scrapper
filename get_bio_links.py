import re
import requests
from bs4 import BeautifulSoup


def get_protein_links(identifier):
    # start web driver
    # load the website in the web driver

    website = "https://go.drugbank.com"
    response = requests.get(
        f"{website}/unearth/q?searcher=bio_entities&query={identifier}")
    soup = BeautifulSoup(response.content, "html.parser")

    # Check if the link leads us to the same EC number that we used in the query
    cards = soup.select(".unearth-search-hit ")

    protein_matches = []

    for card in cards:
        text_area = card.select(".text-muted")[0]
        ec_codes = text_area.find_all("em")
        for ec_code in ec_codes:
            if ec_code.text == identifier:
                protein_selector = card.select(".hit-link")[0]
                bio_id = protein_selector.select(
                    "a[href]")[0].attrs.get("href")
                # Avoid duplicates --> To check if it really does--------------------------------
                if bio_id not in protein_matches:
                    protein_matches.append(bio_id)
    return protein_matches


def get_links_list(identifier):
    """Check if the EC has a match in the database
    Handles both lists of strings and strings

    Args:
        identifier (_str/list_): _description_
    """
    # Check the type
    # If string go get links
    if isinstance(identifier, str):
        setOfLinks = get_protein_links(identifier)
    # If list go get each one at a time
    else:
        setOfLinks = []
        for id in identifier:
            setOfLinks.extend(get_protein_links(id))
    # If the list is not empty add that EC
    if setOfLinks != []:
        with open("files/EClinks.txt", "a") as f:
            f.write(f">{identifier}\n")
            for i in setOfLinks:
                f.write(f"{i}\n")
    else:
        # If empty save into another file
        with open("files/emptyEC.txt", "a") as f:
            f.write(f">{identifier}\n")
            for i in setOfLinks:
                f.write(f"{i}\n")


def get_bio_id_links(filename):
    ec_numbers = []
    with open(filename, "r") as f:
        for line in f.readlines():
            a = line.strip()

            if a[0] == "[":
                parts = re.findall("([1-9][1-9.-]*)", a)
                a = []
                a.extend(parts)
            ec_numbers.append(a)

    # Get the links for the next step
    n = len(ec_numbers)
    for idx, ec in enumerate(ec_numbers):
        get_links_list(ec)
        # print progress
        print(f"{idx+1}/{n}")


def read_ecs():
    ec_dict = {}
    ec = ["pop_me!"]
    ec_name = "pop_me"

    with open("files/EClinks.txt", "r") as f:
        for line in f.readlines():
            if line.strip()[0] != ">":
                ec.append(line.strip())
            else:
                ec_dict[ec_name] = ec
                ec_name = line.strip()[1:]
                ec = []
    ec_dict.pop("pop_me")
    return ec_dict


if __name__ == "__main__":
    get_protein_links("1.4.3.4")
