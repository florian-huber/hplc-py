# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import utils
import scipy.stats
import seaborn as sns
import glob
from hplc.io import load_chromatogram
from hplc.quant import Chromatogram
cor, pal = utils.matplotlib_style()
# Load the representative chromatogram
df = load_chromatogram('data/sample_chromatogram.txt', cols=['time', 'signal'])
dt = np.mean(np.diff(df['time']))

# Add a more pronounced baseline to data to demonstrate power of background subtraction
bg = 2E5 - 5000 * df['time']
df['signal'] += bg
chrom = Chromatogram(df, time_window=[9.5, 20])
peaks = chrom.fit_peaks(approx_peak_width=0.5, buffer=10)

# Generate figure panels showing the stepwise progression of the hplc-py quantification
# algorithm.
fig, ax = plt.subplots(4, 1, figsize=(1.5, 3))
for a in ax:
    a.set_xlim([9.5, 20])
ax[0].plot(chrom.df['time'], chrom.df['signal']/1E5, 'k-', lw=1)
ax[1].plot(chrom.df['time'], chrom.df['signal_corrected']/1E5, 'k-', lw=1)
ax[3].plot(chrom.df['time'], chrom.df['signal_corrected']/1E5, 'k-', lw=1)


for w, v in chrom.window_props.items():
    ax[2].plot(v['time_range'], v['signal']/1E5, lw=1)
for i, p in enumerate(chrom._peak_indices):
    x = chrom.df['time'].values[p]
    y = chrom.df['signal_corrected'].values[p]/1E5
    ax[2].annotate(str(i+1), (x - 0.2, y + 0.01), size=5)

for i in range(len(peaks)):
    ax[3].plot(chrom.df['time'], chrom.unmixed_chromatograms[:, i] /
               1E5, '--', alpha=0.5, lw=1)
    ax[3].fill_between(
        chrom.df['time'], chrom.unmixed_chromatograms[:, i]/1E5, alpha=0.5)

for a in ax:
    a.set_xlabel('time [min] ', fontsize=6)
    a.set_ylabel('signal [a.u.]', fontsize=6)
plt.tight_layout()
plt.savefig('./figures/Fig2_steps.pdf')

# %%
# Load the pure lactose solutions and generate a calibration curve.
# Get list of lactose calibration files and instantiate a calibration dataframe
cal_files = glob.glob('./data/lactose*.csv')
cal_df = pd.DataFrame([])

# Process the chromatograms to get the calibration area
for f in cal_files:
    c = float(f.split('_')[-1].split('.csv')[0])

    # Load the chromatogram
    df = pd.read_csv(f)
    chrom = Chromatogram(df, time_window=[12, 16])

    # Fit the peaks
    _ = chrom.fit_peaks(integration_window=[12, 16], verbose=False)
    peaks = chrom.map_peaks({'lactose': {'retention_time': 13.5}})

    # Set up the calibration dataframe
    _df = pd.DataFrame({'known_conc': c,
                        'retention_time': peaks['retention_time'].values[0],
                        'area': peaks['area'].values[0],
                        'scale': peaks['scale'].values[0],
                        'skew': peaks['skew'].values[0]}, index=[0])
    cal_df = pd.concat([cal_df, _df], sort=False)

# %%
# Compute the calibration curve parameters
popt = scipy.stats.linregress(cal_df['known_conc'], cal_df['area'])
cmap = sns.color_palette('Blues_r', n_colors=11)
concs = [float(f.split('_')[-1][:-4]) for f in cal_files]
mapper = {c: cmap[i] for i, c in enumerate(np.sort(concs))}


fig, ax = plt.subplots(1, 2, figsize=(3.5, 1.5))
ax[0].set_xlim([13, 15])
ax[0].set_xlabel('retention time [min]', fontsize=6)
ax[0].set_ylabel(r'signal intensity [$\times 10^4$ a.u.]', fontsize=6)

ax[1].set_xlabel('known lactose\nconcentration [mM]', fontsize=6)
ax[1].set_ylabel('integrated signal\nintensity' +
                 r' [$\times 10^6$ a.u.]', fontsize=6)
ax[1].set_ylim([0, 1.5])

# Plot the calibration chromatograms
for i, f in enumerate(cal_files):
    c = float(f.split('_')[-1][:-4])
    df = pd.read_csv(f)
    ax[0].plot(df['time'], (df['signal']-700)/1E4, lw=1,
               color=mapper[c], label='__nolegend__')
for k, v in mapper.items():
    ax[0].plot([], [], '-', lw=3, color=v, label=f'{k}')
leg = ax[0].legend(handlelength=0.5, fontsize=5, title='lactose\n  [mM]')
leg.get_title().set_fontsize(5)


# Plot the calibration curve fit
c_range = np.linspace(0, 9, 100)
fit = popt[1] + popt[0] * c_range
ax[1].plot(c_range, fit/1E6, '-', color=cor['dark_blue'], lw=1, zorder=1000)
ax[1].scatter(cal_df['known_conc'], cal_df['area']/1E6, c=[mapper[c]
              for c in cal_df['known_conc'].values], marker='o', s=30, ec=cor['dark_blue'])
plt.savefig('./figures/Fig2_cal_curve.pdf')
