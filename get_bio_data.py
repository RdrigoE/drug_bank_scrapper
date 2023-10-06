from typing import TypedDict
from get_bio_links import bio_entity
import json
import requests
from bs4 import BeautifulSoup
import csv


class Protein(TypedDict):
    EC: str
    Name: str
    Uniprot_ID: str
    Organism: str


class DrugRelation(TypedDict):
    DrugBank_ID: str
    Name: str
    Drug_Group: str
    Pharmacological_Action: str
    Actions: str


def get_protein_info(soup_body, ec):
    protein_info: list[str] = []

    for body in soup_body:
        for info in body.select("td"):
            protein_info.append(info.string)

    proteins: dict[str, Protein] = {}

    for i in range(0, len(protein_info), 3):

        uniprot_id = protein_info[i+1]
        if protein_info[i+1] and len(uniprot_id) == 6 and uniprot_id.isupper():
            protein = Protein(
                EC=ec,
                Name=protein_info[i],
                Uniprot_ID=protein_info[i+1],
                Organism=protein_info[i+2]
            )
            proteins[f"Protein{i}"] = protein

    return proteins


def get_protein_table(proteins: dict[str, Protein]):
    ec_table = []
    for protein in proteins:
        if ',' in proteins[protein]["EC"]:
            proteins[protein]["EC"] = json.loads(
                proteins[protein]["EC"].replace("'", '"'))
            for j in range(len(proteins[protein]["EC"])):
                obj = (proteins[protein]["EC"][j],
                       proteins[protein]["Uniprot_ID"],
                       proteins[protein]["Name"].replace("'", ""))
                if obj not in ec_table:
                    ec_table.append(obj)
        else:
            obj = (proteins[protein]["EC"],
                   proteins[protein]["Uniprot_ID"],
                   proteins[protein]["Name"].replace("'", ""))
            if obj not in ec_table:
                ec_table.append(obj)
    return ec_table


def get_drug_info(soup_body):
    drug_relations = []

    for drug_r in soup_body:
        for j in drug_r.select("td"):
            drug_relations.append(j.string)

    drug_relations_dict = {}

    for i in range(0, len(drug_relations), 6):
        relation = DrugRelation(
            DrugBank_ID=drug_relations[i],
            Name=drug_relations[i+1],
            Drug_Group=drug_relations[i+2],
            Pharmacological_Action=drug_relations[i+3],
            Actions=drug_relations[i+4],
        )
        if relation["Actions"] is None:
            relation["Actions"] = "Null"
        drug_relations_dict[f"relation{i}"] = relation
    return drug_relations_dict


def get_drug_table(drugs):
    drug_table = []
    for drug in drugs:
        obj = [drugs[drug]["DrugBank_ID"],
               drugs[drug]["Name"],
               drugs[drug]["Pharmacological_Action"],
               drugs[drug]["Actions"]]
        if obj not in drug_table:
            drug_table.append(obj)
    return drug_table


def get_drug_relationship_table(drugs, proteins):
    drug_relationship = []
    for relationship in drugs:
        if "," in drugs[relationship]["Drug_Group"]:
            drug_groups = drugs[relationship]["Drug_Group"].split(
                ', ')
            for drug_group in drug_groups:
                # this is a bad way to filter between tables with ec and lists of ecs
                if len(proteins['Protein0']["EC"]) < 7:
                    # For each ec in the list create the object
                    for j in range(len(proteins['Protein0']["EC"])):
                        obj = [proteins['Protein0']["EC"][j],
                               proteins['Protein0']["Uniprot_ID"],
                               drugs[relationship]["DrugBank_ID"],
                               drug_group]
                # if it is not a list just create the object
                else:
                    obj = [proteins['Protein0']["EC"],
                           proteins['Protein0']["Uniprot_ID"],
                           drugs[relationship]["DrugBank_ID"],
                           drug_group]
                # If the object in not in the LIST we append it
                if obj not in drug_relationship:
                    drug_relationship.append(obj)

    return drug_relationship


def get_single_biodata(link: str, ec):

    page = requests.get(link)

    soup = BeautifulSoup(page.content, 'html.parser')

    proteins = get_protein_info(soup.select("tbody"), ec)
    ec_table = get_protein_table(proteins)

    drugs = get_drug_info(soup.select("tbody")[1])
    drug_table = get_drug_table(drugs)

    drug_relationship_table = get_drug_relationship_table(drugs, proteins)

    with open("files/DRUG_TABLE.csv", "a", newline='') as f:
        writer = csv.writer(f)
        for i in drug_table:
            writer.writerow(i)

    # Write the Protein csv
    with open("files/ECTABLE.csv", "a", newline='') as f:
        writer = csv.writer(f)
        for i in ec_table:
            writer.writerow(i)
    # Write the Drug state csv
    with open("files/DRUG_RELATIONSHIP.csv", "a", newline='') as f:
        writer = csv.writer(f)
        for i in drug_relationship_table:
            writer.writerow(i)


def get_bio_data(ec_codes: dict[str, list[bio_entity]]):
    website = "https://go.drugbank.com"
    for code, entities in ec_codes.items():
        for entity in entities:
            get_single_biodata(website + entity, code)


if __name__ == "__main__":
    get_single_biodata("https://go.drugbank.com" +
                       "/bio_entities/BE0002196", "1.4.3.4")
