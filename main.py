from database import get_approved_protein_drugs
from get_bio_data import get_bio_data
from get_bio_links import get_bio_id_links, read_ecs
from get_ec_numbers import define_ec_numbers
import utils
import sys


def get_info(model, filename):

    # Get the EC numbers *File is created
    db_file_name = "files/EC_NAME.csv"
    define_ec_numbers(model, filename, db_file_name)

    # Get the str out of the lists and Recreate lists of combined EC
    get_bio_id_links(filename)
    ec_codes = read_ecs()

    # Get the data for each list of str of ECS

    get_bio_data(ec_codes)
    #
    # # Remove duplicates of each list
    utils.remove_duplicates("files/EC_NAME.csv")
    utils.remove_duplicates("files/DRUG_TABLE.csv")
    utils.remove_duplicates("files/ECTABLE.csv")
    utils.remove_duplicates("files/DRUG_RELATIONSHIP.csv")

    get_approved_protein_drugs()


def main():
    get_info(sys.argv[1], "files/data.txt")


if __name__ == "__main__":
    main()
