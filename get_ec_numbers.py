from cobra.io import read_sbml_model
import cobra
import csv


def write_reactions(filename, reactions):
    with open(filename, "w") as f:
        for reaction in reactions:
            f.write(f"{reaction}\n")


def write_reactions_name(filename: str, reactions_name: list[tuple[str, str]]) -> None:
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(reactions_name)


def add_reaction_name(reactions_name: list[tuple[str, str]],
                      reaction: cobra.Reaction) -> None:
    if isinstance(reaction.annotation['ec-code'], list):
        for code in reaction.annotation['ec-code']:
            reactions_name.append(
                (code, reaction.name.replace("'", "")))
    else:
        reactions_name.append(
            (reaction.annotation['ec-code'], reaction.name.replace("'", "")))


def get_ec_numbers(model_path: str):
    model = read_sbml_model(model_path)

    reactions: list[str | list[str]] = []
    reactions_name: list[tuple[str, str]] = []

    for reaction in cobra.flux_analysis.variability.find_essential_reactions(model):
        if reaction.annotation.get('ec-code') is None:
            continue

        reactions.append(reaction.annotation['ec-code'])

        add_reaction_name(reactions_name, reaction)

    return reactions, reactions_name


def define_ec_numbers(model_path, filename, db_file_name):
    reactions, reactions_name = get_ec_numbers(model_path)
    write_reactions(filename, reactions)
    write_reactions_name(db_file_name, reactions_name)


if __name__ == '__main__':
    define_ec_numbers("models/iEK1008.xml",
                      "files/my_ec_numbers",
                      "files/EC_NAME.csv")
