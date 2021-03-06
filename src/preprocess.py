import os
import pandas as pd


def main(input_path):
    # new version of preprocess only handles singleton file including all chroms
    if os.path.isfile(input_path):
        raw_summary = load_formatted_csv(input_path)
    else:
        raise IsADirectoryError('input path should be formatted singletons csv')

    # filter indel and heterozygous mutations
    filtered_summary = filter_raw_data(raw_summary)
    # counts of 3-mer mutations split by haplotype for each strain
    # includes epoch data
    mutation_strain_df = mutations_by_strains_df(filtered_summary)

    return raw_summary, filtered_summary, mutation_strain_df


def load_formatted_csv(f_name):
    df = pd.read_csv(f_name, sep='\t', header=0, index_col=None)
    df.set_index('expanded_strain', inplace=True)

    return df


def filter_raw_data(df, remove_hetero=True, remove_homo=False):
    # remove indel mutations
    df = df[~df['kmer'].str.contains('indel')]

    # remove heterozygous mutations
    if remove_hetero:
        df = df[df['gt'] == 2]
    if remove_homo:
        df = df[df['gt'] == 1]

    return df


def mutations_by_strains_df(filtered_df):
    # list of strain names
    strains = filtered_df.index.unique()
    # list of mutation counts by strain as Series
    mut_strain = []

    for str in strains:
        # create a sub df of mutations for each strain
        per_strain_df = filtered_df.loc[[str], :]
        # divide per_strain_df into two new ones by haplotype
        bl_strain_df = per_strain_df[per_strain_df['haplotype'] == 0]
        dba_strain_df = per_strain_df[per_strain_df['haplotype'] == 1]
        # find the counts for each mutation type by haplotype
        bl_snv_counts = bl_strain_df['kmer'].value_counts()
        dba_snv_counts = dba_strain_df['kmer'].value_counts()
        # concat the per haplotype counts with a multiindex
        strain_snv_counts = pd.concat([bl_snv_counts, dba_snv_counts], keys=['BL', 'DBA'],
                                      names=['haplotype', 'kmer'])
        # label the counts with the strain name
        strain_snv_counts.rename(str, inplace=True)
        # append to list, each item is a unique strain
        mut_strain.append(strain_snv_counts)

    # concat so that columns are strains and rows are kmers x haplotype
    mut_strain_df = pd.concat(mut_strain, axis=1)
    # because these are counts fill NaN as 0
    mut_strain_df.fillna(0, inplace=True)

    # split multiindex from kmer to the SNV and flanking bases
    kmer_index = mut_strain_df.index.get_level_values('kmer')
    haplo_index = mut_strain_df.index.get_level_values('haplotype')
    multi_index = [kmer_index.str[1] + '>' + kmer_index.str[-2], kmer_index.str[0], kmer_index.str[-1], haplo_index]
    mut_strain_df.index = pd.MultiIndex.from_arrays(multi_index, names=['snv', '5\'', '3\'', 'ht'])

    # sort index and columns
    mut_strain_df.sort_index(axis=0, level=0, inplace=True)
    mut_strain_df.sort_index(axis=1, inplace=True)

    return mut_strain_df
