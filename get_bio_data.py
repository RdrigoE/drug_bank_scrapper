import json
import requests
from bs4 import BeautifulSoup
import csv


def get_single_biodata(link, ec):
    # Get the Link
    page = requests.get(link)
    # Pase the content of the request object
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get Info for the Protein Table
    protein_info = []

    for body in soup.select("tbody"):
        for info in body.select("td"):
            protein_info.append(info.string)

    proteins_object = {}

    for i in range(0, len(protein_info), 3):
        protein = {
            "EC": ec,
            "Name": protein_info[i],
            "Uniprot_ID": protein_info[i+1],
            "Organism": protein_info[i+2]
        }
        proteins_object[f"Protein{i}"] = protein

    # Get Info for the Drug and Drug RelationShip
    drug_relations = []

    for drug_r in soup.select("tbody")[1]:
        for j in drug_r.select("td"):
            drug_relations.append(j.string)

    drug_relations_obj = {}
    for i in range(0, len(drug_relations), 6):
        relation = {
            "DrugBank_ID": drug_relations[i],
            "Name": drug_relations[i+1],
            "Drug_Group": drug_relations[i+2],
            "Pharmacological Action?": drug_relations[i+3],
            "Actions": drug_relations[i+4],
        }
        if relation["Actions"] is None:
            relation["Actions"] = "Null"
        drug_relations_obj[f"relation{i}"] = relation

    ###PROTEIN TABLE###
    ec_table = []
    for protein in proteins_object:
        if len(proteins_object[protein]["EC"]) > 11:
            proteins_object[protein]["EC"] = json.loads(
                proteins_object[protein]["EC"].replace("'", '"'))
            for j in range(len(proteins_object[protein]["EC"])):
                obj = [proteins_object[protein]["EC"][j],
                       proteins_object[protein]["Uniprot_ID"],
                       proteins_object[protein]["Name"].replace("'", "")]
                if obj not in ec_table:
                    ec_table.append(obj)
        else:
            obj = [proteins_object[protein]["EC"],
                   proteins_object[protein]["Uniprot_ID"],
                   proteins_object[protein]["Name"].replace("'", "")]
            if obj not in ec_table:
                ec_table.append(obj)
    ###Drug TABLE###
    drug_table = []
    for drug in drug_relations_obj:
        obj = [drug_relations_obj[drug]["DrugBank_ID"],
               drug_relations_obj[drug]["Name"],
               drug_relations_obj[drug]["Pharmacological Action?"],
               drug_relations_obj[drug]["Actions"]]
        if obj not in drug_table:
            drug_table.append(obj)

    ###Drug STATE###

    drug_relationship = []
    for relationship in drug_relations_obj:
        if "," in drug_relations_obj[relationship]["Drug_Group"]:
            iterable = drug_relations_obj[relationship]["Drug_Group"].split(
                ', ')
            for x in iterable:
                # this is a bad way to filter between tables with ec and lists of ecs
                if len(proteins_object['Protein0']["EC"]) < 7:
                    # For each ec in the list create the object
                    for j in range(len(proteins_object['Protein0']["EC"])):
                        obj = [proteins_object['Protein0']["EC"][j],
                               proteins_object['Protein0']["Uniprot_ID"],
                               drug_relations_obj[relationship]["DrugBank_ID"],
                               x]
                # if it is not a list just create the object
                else:
                    obj = [proteins_object['Protein0']["EC"],
                           proteins_object['Protein0']["Uniprot_ID"],
                           drug_relations_obj[relationship]["DrugBank_ID"],
                           x]
                # If the object in not in the LIST we append it
                if obj not in drug_relationship:
                    drug_relationship.append(obj)

    # Write the Drug csv
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
        for i in drug_relationship:
            writer.writerow(i)


def get_bio_data(ec_codes):
    website = "https://go.drugbank.com"
    total = len(ec_codes.keys())
    count = 0
    for code in ec_codes:
        for reference in ec_codes[code]:
            print(f"{count}/{total}")
            get_single_biodata(website + reference, code)
            count += 1


if __name__ == "__main__":
    get_single_biodata("https://go.drugbank.com" +
                       "/bio_entities/BE0002196", "1.4.3.4")
