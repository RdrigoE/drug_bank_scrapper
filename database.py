import csv
import psycopg2
import utils

# Create user with superuser (s) permisions
# sudo -u postgres createuser -s  python_script \--pwprompt
# establishing the connection


def create_db():
    con = psycopg2.connect(
        database="postgres",
        user='python_script',
        password='password',
        host='127.0.0.1',
        port='5432'
    )
    con.autocommit = True

    # Creating a cursor object using the cursor() method
    cursor = con.cursor()

    # Preparing query to create a database
    sql = '''DROP DATABASE IF EXISTS drugbank WITH (FORCE);'''
    cursor.execute(sql)
    sql = '''CREATE database drugbank;'''
    # Creating a database
    cursor.execute(sql)

    print("Database created successfully.")

    # Closing the connection
    con.close()


def populate_db():
    # Establish database connection
    con = psycopg2.connect(host="127.0.0.1",
                           port="5432",
                           user="python_script",
                           password="password",
                           database="drugbank")
    con.autocommit = True
    # Get a database cursor
    cur = con.cursor()

    sql = '''
    create table EC (
        EC_NUMBER            VARCHAR(50)          not null UNIQUE,
        NAME                 varchar(200)         null,
        constraint PK_EC primary key (EC_NUMBER)
    )
    '''
    cur.execute(sql)

    sql = '''
    create table PROTEIN (
    UNIPROT_ID           varchar(50)           not null,
    EC_NUMBER            VARCHAR(50)          not null,
    NAME                 varchar(200)          null,
    constraint PK_PROTEIN primary key (UNIPROT_ID)
    )
    '''
    cur.execute(sql)

    sql = '''
    create table DRUG (
    DRUG_BANK_ID               VARCHAR(15)          not null,
    NAME                       varchar(200)         null,
    PHARMACOLOGICAL_ACTION     varchar(50)          null,
    ACTION                     varchar(50)          null,
    constraint PK_DRUG primary key (DRUG_BANK_ID)
    );
    '''
    cur.execute(sql)

    sql = '''
    create table DRUGPROTEIN (
    EC_NUMBER            VARCHAR(50)          not null,   
    DRUG_BANK_ID         VARCHAR(50)          not null,
    UNIPROT_ID           varchar(50)          not null,
    DRUG_GROUP           VARCHAR(50)          not null,
    constraint PK_DRUGPROTEIN primary key (EC_NUMBER, DRUG_BANK_ID, UNIPROT_ID, DRUG_GROUP)
    );
    '''
    cur.execute(sql)

    sql = '''
    alter table PROTEIN
    add constraint FK_PROTEIN foreign key (EC_NUMBER)
        references EC (EC_NUMBER)
    ;
    '''
    cur.execute(sql)

    sql = '''
    alter table DRUGPROTEIN
    add constraint FK_PROTEIN_DRUG1 foreign key (EC_NUMBER)
        references EC (EC_NUMBER)
    ;
    '''
    cur.execute(sql)

    sql = '''
    alter table DRUGPROTEIN
    add constraint FK_PROTEIN_DRUG2 foreign key (UNIPROT_ID)
        references PROTEIN (UNIPROT_ID)
    ;
    '''
    cur.execute(sql)

    sql = '''
    alter table DRUGPROTEIN
    add constraint FK_PROTEIN_DRUG3 foreign key (DRUG_BANK_ID)
        references DRUG (DRUG_BANK_ID)
    ;
    '''
    cur.execute(sql)
    con.commit()

    ec_names = utils.get_list_csv('./files/EC_NAME.csv')
    for ec in ec_names:
        try:
            cur.execute(
                f"INSERT INTO EC (EC_NUMBER,NAME) VALUES ('{ec[0]}','{ec[1]}')")
        except Exception as e:
            print(e)

    # write the script to sql: Protein
    proteins = utils.get_list_csv("./files/ECTABLE.csv")
    for protein in proteins:
        try:
            protein[2] = protein[2].replace("'", "")
            cur.execute(
                f"INSERT INTO PROTEIN (EC_NUMBER,UNIPROT_ID,NAME) VALUES ('{protein[0]}','{protein[1]}','{protein[2]}')")
        except Exception as e:
            # ... PRINT THE ERROR MESSAGE ... #
            print(e)
    # write the script to sql: Drug
    drugs = utils.get_list_csv("./files/DRUG_TABLE.csv")

    for drug in drugs:
        try:
            drug[1] = drug[1].replace("'", "")
            cur.execute(
                f"INSERT INTO DRUG (DRUG_BANK_ID,NAME,PHARMACOLOGICAL_ACTION,ACTION) VALUES ('{drug[0]}','{drug[1]}','{drug[2]}','{drug[3]}')")
        except Exception as e:
            print(e)

    # write the script to sql: Drug State
    drug_proteins = utils.get_list_csv("./files/DRUG_RELATIONSHIP.csv")

    for drug_p in drug_proteins:

        try:
            drug_p[1] = drug_p[1].replace("'", "")
            cur.execute(
                f"INSERT INTO drugprotein (EC_NUMBER,UNIPROT_ID,DRUG_BANK_ID,DRUG_GROUP) VALUES ('{drug_p[0]}','{drug_p[1]}','{drug_p[2]}','{drug_p[3]}')")
        except Exception as e:
            print(e)

    # Commit the data
    con.commit()
    cur.execute("""SELECT P.EC_NUMBER, P.UNIPROT_ID, P.NAME, D.DRUG_BANK_ID, D.NAME, DR.DRUG_GROUP,D.PHARMACOLOGICAL_ACTION, D.ACTION
                    FROM DRUGPROTEIN DR 
                    INNER JOIN PROTEIN P ON P.EC_NUMBER=DR.EC_NUMBER AND P.UNIPROT_ID = DR.UNIPROT_ID
                    INNER JOIN DRUG D 
                    ON DR.DRUG_BANK_ID = D.DRUG_BANK_ID 
                    WHERE DR.DRUG_GROUP = 'approved'
                    AND D.PHARMACOLOGICAL_ACTION = 'yes' AND D.ACTION = 'inhibitor'""")
    result = cur.fetchall()
    for i, _ in enumerate(result):
        result[i] = list(result[i])
        # result[i].append(f"https://www.brenda-enzymes.org/enzyme.php?ecno={result[i][0]}#APPLICATION")
        # result[i].append(f"https://www.uniprot.org/uniprot/{result[i][1]}")
    with open("./output/approved.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(result)

    cur.execute("""SELECT P.EC_NUMBER, P.UNIPROT_ID, P.NAME, D.DRUG_BANK_ID, D.NAME, DR.DRUG_GROUP,D.PHARMACOLOGICAL_ACTION, D.ACTION
                    FROM DRUGPROTEIN DR 
                    INNER JOIN PROTEIN P ON P.EC_NUMBER=DR.EC_NUMBER AND P.UNIPROT_ID = DR.UNIPROT_ID
                    INNER JOIN DRUG D 
                    ON DR.DRUG_BANK_ID = D.DRUG_BANK_ID 
                    WHERE DR.DRUG_GROUP = 'experimental' AND D.ACTION = 'inhibitor'
                """)
    result = cur.fetchall()
    for i, _ in enumerate(result):
        result[i] = list(result[i])
        # result[i].append(f"https://www.brenda-enzymes.org/enzyme.php?ecno={result[i][0]}#APPLICATION")
        # result[i].append(f"https://www.uniprot.org/uniprot/{result[i][1]}")
    with open("./output/experimental.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(result)

    cur.execute("""SELECT P.EC_NUMBER, P.UNIPROT_ID, P.NAME, D.DRUG_BANK_ID, D.NAME, DR.DRUG_GROUP,D.PHARMACOLOGICAL_ACTION, D.ACTION
                    FROM DRUGPROTEIN DR 
                    INNER JOIN PROTEIN P ON P.EC_NUMBER=DR.EC_NUMBER AND P.UNIPROT_ID = DR.UNIPROT_ID
                    INNER JOIN DRUG D 
                    ON DR.DRUG_BANK_ID = D.DRUG_BANK_ID 
                    WHERE DR.DRUG_GROUP = 'investigational' AND D.ACTION = 'inhibitor' AND D.PHARMACOLOGICAL_ACTION = 'unknown'
                """)
    result = cur.fetchall()
    for i, _ in enumerate(result):
        result[i] = list(result[i])
        # result[i].append(f"https://www.brenda-enzymes.org/enzyme.php?ecno={result[i][0]}#APPLICATION")
        # result[i].append(f"https://www.uniprot.org/uniprot/{result[i][1]}")
    with open("./output/investigational.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(result)

    # Close our database connections
    cur.close()
    con.close()


def get_approved_protein_drugs():
    create_db()
    populate_db()


if __name__ == '__main__':
    get_approved_protein_drugs()
