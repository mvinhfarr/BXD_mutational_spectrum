import os
import pandas as pd
import matplotlib.pyplot as plt

import preprocess
import visualize

os.chdir('..')

data_dir = 'data/per_chr_singleton'

results_df = 'out/dfs/'
results_figs = 'out/figs/'

# preprocess.main(data_dir, results_df)

raw_df = pd.read_csv(results_df+'raw_singleton_summary', index_col=0)
filtered_df = pd.read_csv(results_df+'filtered_singletons', index_col=0)
formatted_df = pd.read_csv(results_df+'formatted_singletons', index_col=0)
mutation_strain_df = pd.read_csv(results_df+'mutation_strains', index_col=[0, 1, 2, 3])

# snv_df, bl_df, dba_df = visualize.mutation_spectrum_barchartsv1(mutations_strains,
# show=True, save=False, results_dir=results_figs)

snv_frac_per_strain, snv_frac_strain_avg, ht_snv_frac_strain_avg, snv_tot_frac, ht_snv_tot_frac = \
    visualize.mutation_spectrum_barcharts(mutation_strain_df, show=False, save=False, results_dir=results_figs)

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2)

temp = mutation_strain_df.sum(axis=1)
temp.unstack([1]).plot(kind='bar', ax=ax3, stacked=True)

plt.show()

