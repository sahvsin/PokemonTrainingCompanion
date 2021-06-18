from gen_reader import *




def build_pkmn_df(gen):

    path = "CSV/statCSV/" + gen + ".csv"

    if gen == "genI":
        return genI_csv2df(path)
    else:
        return csv2df(path)



def get_names(pkmn_df):

    return pkmn_df['Name'].tolist()



def get_base_stats(pkmn_df, pkmn_name, gen, stat_labels):

    return pkmn_df.loc[pkmn_df['Name'] == pkmn_name, stat_labels].values.tolist()



def build_natures_df():

    path = "CSV/" + "natures" + ".csv"
    return nature_csv2df(path)



def get_stat_mods(natures_df, nature, stat_labels):

    return natures_df.loc[natures_df['Nature'] == nature, stat_labels].values.tolist()
