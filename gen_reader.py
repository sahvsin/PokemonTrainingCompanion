import pandas as pd





def genI_csv2df(csv_file):
    '''
    Inputs:
    csv_file - csv file to get the data from

    Outputs:
    pandas dataframe containing the data in the csv
    '''

    labels = ["#", "Name", "Type 1", "Type 2", "Total", "HP", "Attack", "Defense", "Special", "Speed"]
    return pd.read_csv(csv_file, names=labels)





def csv2df(csv_file):
    '''
    Inputs:
    csv_file - csv file to get the data from

    Outputs:
    pandas dataframe containing the data in the csv
    '''

    labels = ["#", "Name", "Type 1", "Type 2", "Total", "HP", "Attack", "Defense", "Special Attack", "Special Defense", "Speed"]
    return pd.read_csv(csv_file, names=labels)




def nature_csv2df(csv_file):
    '''
    Inputs:
    csv_file - csv file to get the data from

    Outputs:
    pandas dataframe containing the data in the csv
    '''

    labels = ["Nature", "Attack", "Defense", "Special Attack", "Special Defense", "Speed"]
    return pd.read_csv(csv_file, names=labels)

