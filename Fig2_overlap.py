# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import scipy.stats
import utils
from hplc.quant import Chromatogram
cor, pal = utils.matplotlib_style()

# Get list of lactose calibration files and instantiate a calibration dataframe
cal_files = glob.glob('./data/lactose*mM.txt')
cal_df = pd.DataFrame([])

# Process the chromatograms to get the calibration area
for f in cal_files:
    c = float(f.split('_')[-1].split('mM.txt')[0])

    # Load the chromatogram
    df = pd.read_csv(f)
    chrom = Chromatogram(df, time_window=[12, 15])

    # Fit the peaks
    _ = chrom.fit_peaks(integration_window=[12, 16], verbose=False)
    peaks = chrom.map_peaks({'lactose': {'retention_time': 13.5}})

    # Set up the calibration dataframe
    _df = pd.DataFrame({'known_conc': c,
                        'retention_time': peaks['retention_time'].values[0],
                        'area': peaks['area'].values[0]}, index=[0])
    cal_df = pd.concat([cal_df, _df], sort=False)

# Compute the calibration curve parameters
popt = scipy.stats.linregress(cal_df['known_conc'], cal_df['area'])

# %%
# Get the peak parameters of the baseline peak
base_df = pd.read_csv('./data/baseline.txt')
base_chrom = Chromatogram(base_df, time_window=[12, 15])
base_peaks = base_chrom.fit_peaks(integration_window=[12, 16], verbose=False)
base_chrom.show()
base_peaks

# %%
constraints = {}
for g, d in base_peaks.groupby('peak_id'):
    constraints[d['retention_time'].values[0]] = {
        'amplitude': d['amplitude'].values[0] * np.array([0.95, 1.05])}
constraints[cal_df['retention_time'].mean()] = {}
constraints

# %%
# Load the test files
test_files = glob.glob('./data/*phosphate.txt')
df = pd.read_csv(test_files[-1])
chrom = Chromatogram(df)
peaks = chrom.fit_peaks(known_peaks=[13.5, 15])
chrom.show()
