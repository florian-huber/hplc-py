#%%
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import utils
import scipy.stats
from hplc.io import load_chromatogram
from hplc.quant import Chromatogram
cor, pal  = utils.matplotlib_style()
df = load_chromatogram('data/sample_chromatogram.txt', cols=['time','signal'])
dt = np.mean(np.diff(df['time']))

# Add a more pronounced baseline to data to demonstrate power of background subtraction
bg = 2E5 - 5000 * df['time']
df['signal'] += bg
chrom = Chromatogram(df, time_window=[9.5, 20])
peaks = chrom.fit_peaks(approx_peak_width=0.5, buffer=10)
fig, ax = plt.subplots(4, 1, figsize=(1.5, 3))
for a in ax:
    a.set_xlim([9.5, 20])
ax[0].plot(chrom.df['time'], chrom.df['signal']/1E5, 'k-', lw=1)
ax[1].plot(chrom.df['time'], chrom.df['signal_corrected']/1E5, 'k-', lw=1)
ax[3].plot(chrom.df['time'], chrom.df['signal_corrected']/1E5, 'k-', lw=1)


for w,v in chrom.window_props.items():
    ax[2].plot(v['time_range'], v['signal']/1E5, lw=1)
for i, p in enumerate(chrom._peak_indices):
    x = chrom.df['time'].values[p]
    y = chrom.df['signal_corrected'].values[p]/1E5
    ax[2].annotate(str(i+1), (x - 0.2, y + 0.01), size=5)

for i in range(len(peaks)):
    ax[3].plot(chrom.df['time'], chrom.unmixed_chromatograms[:, i]/1E5, '--', alpha=0.5, lw=1)
    ax[3].fill_between(chrom.df['time'], chrom.unmixed_chromatograms[:, i]/1E5, alpha=0.5)

for a in ax:
    a.set_xlabel('time [min] ', fontsize=6)
    a.set_ylabel('signal [a.u.]', fontsize=6)
plt.tight_layout()
plt.savefig('./figures/Fig2_steps.pdf')