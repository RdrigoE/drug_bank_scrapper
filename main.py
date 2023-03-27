from database import get_approved_protein_drugs
from get_bio_data import get_bio_data
from get_bio_links import get_bio_id_links, read_ecs
from get_ec_numbers import get_ec_numbers
import utils


def get_info(model, filename):

    # Get the EC numbers *File is created
    get_ec_numbers(model, filename)
    # Get the str out of the lists and Recreate lists of combined EC
    get_bio_id_links(filename)
    ec_codes = read_ecs()

    # Get the data for each list of str of ECS
    get_bio_data(ec_codes)

    # Remove duplicates of each list
    utils.remove_duplicates("files/EC_NAME.csv")
    utils.remove_duplicates("files/DRUG_TABLE.csv")
    utils.remove_duplicates("files/ECTABLE.csv")
    utils.remove_duplicates("files/DRUG_RELATIONSHIP.csv")
    #
    # write SQL
    get_approved_protein_drugs()


if __name__ == "__main__":
    get_info("models/iEK1008.xml", "files/iEK1008.txt")
