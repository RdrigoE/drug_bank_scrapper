from cobra.io import read_sbml_model
import cobra
import csv


def get_ec_numbers(model, filename):

    # Read the model
    model = read_sbml_model(model)

    # Get reaction EC_NUMBER and NAME
    reactions = []
    reactions_name = []
    for reaction in cobra.flux_analysis.variability.find_essential_reactions(model):
        try:
            reactions.append(reaction.annotation['ec-code'])
            if type(reaction.annotation['ec-code']) == type([]):
                for code in reaction.annotation['ec-code']:
                    reactions_name.append(
                        [code, reaction.name.replace("'", "")])
            else:
                reactions_name.append(
                    [reaction.annotation['ec-code'], reaction.name.replace("'", "")])
        except:
            pass
    # Write the EC numbers for further use in selenium
    with open(filename, "w") as f:
        for reaction in reactions:
            f.write(f"{reaction}\n")

    # Write the EC numbers and name for further use building the database
    with open("files/EC_NAME.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(reactions_name)

    print(f"All Done! File {filename} sucessufuly created!")


if __name__ == '__main__':
    get_ec_numbers('models/iEK1008.xml', "files/my_ec_numbers")
