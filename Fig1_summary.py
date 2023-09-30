# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats
import utils
from hplc.quant import Chromatogram
cor, pal = utils.matplotlib_style()
# Set up a simulated dataset with three compounds, two of which have similar
# retention times
dt = 0.01
locs = [6, 9.5, 28]
scales = [1, 0.75, 2.5]
skews = [0, -0.10, -8.0]
amps = [60, 30, 90]
time_range = np.arange(0, 35, dt)
sig = np.zeros((len(time_range), len(locs)+1))
for i in range(len(locs)):
    sig[:, i] = amps[i] * \
        scipy.stats.skewnorm(skews[i], loc=locs[i],
                             scale=scales[i]).pdf(time_range)

fig, ax = plt.subplots(1, 1, figsize=(2.5, 2))
ax.plot(time_range, np.sum(sig, axis=1), lw=1, color='k')
ax.set_xlabel('time', fontsize=6)
ax.set_ylabel('signal', fontsize=6)
ax.set_ylim([-0.5, 35])
ax.set_yticklabels(['','',''])
ax.set_xticklabels(['','',''])
plt.savefig('./figures/Fig1_synthetic_chromatogram.pdf')

#%%
# Save the example
_df = pd.DataFrame(np.array([time_range, np.round(np.sum(sig, axis=1), decimals=3)]).T, columns=['time','signal'])
_df.to_csv('./chromatogram.txt',index=False)
#%%
from hplc.io import load_chromatogram
from hplc.quant import Chromatogram
data = load_chromatogram('chromatogram.txt', 
                         cols=['time','signal'])
chrom = Chromatogram(data) 
peaks = chrom.fit_peaks()
chrom.show()


plt.savefig('./chromatogram.pdf')