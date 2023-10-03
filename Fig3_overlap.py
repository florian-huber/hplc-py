# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import scipy.stats
import seaborn as sns
import utils
from hplc.quant import Chromatogram
cor, pal = utils.matplotlib_style()

# Make a figure showing chromatograms for lactose in water, the baseline, and
# the mixture. Subtracting 700 as rough baseline correction for visualization.
samp = pd.read_csv('./data/lactose_mM_8.csv')
samp['signal'] -= 700
samp['signal'] *= 1E-4
buff = pd.read_csv('./data/buffer_3.csv')
buff['signal'] -= 700
buff['signal'] *= 1E-4
mix = pd.read_csv('./data/buffer_lactose_mM_8.csv')
mix['signal'] -= 700
mix['signal'] *= 1E-4


fig, ax = plt.subplots(1, 1, figsize=(3, 1.5))
ax.set_xlim([12, 16])

ax.plot(mix['time'], mix['signal'], '--', lw=1.5,
        color=cor['primary_black'], zorder=1000)


ax.fill_between(buff['time'], buff['signal'],
                color=cor['pale_purple'], alpha=0.5)
ax.plot(buff['time'], buff['signal'], lw=1, color=cor['purple'])

ax.fill_between(samp['time'], samp['signal'],
                color=cor['pale_blue'], alpha=0.5)
ax.plot(samp['time'], samp['signal'], lw=1, color=cor['blue'])
ax.set_xlabel('retention time [min]', fontsize=6)
ax.set_ylabel(r'signal intensity [$\times 10^4$ a.u.]', fontsize=6)
plt.savefig('./figures/Fig3_compound_overlaps.pdf', bbox_inches='tight')

# %%
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

# Load a buffer calibration file and fit the peak
buff = pd.read_csv('./data/buffer_1.csv')
buff_chrom = Chromatogram(buff, time_window=[12, 16])
buff_peak = buff_chrom.fit_peaks()

# Make a figure of all of the calibration chromatograms for lactose in water,
# the calibration curve, and a fit baseline chromatogram with parameters
fig, ax = plt.subplots(1, 3, figsize=(4.5, 1.4))
ax[0].set_xlim([13, 15])
ax[0].set_xlabel('retention time [min]', fontsize=6)
ax[0].set_ylabel(r'signal intensity [$\times 10^4$ a.u.]', fontsize=6)

ax[1].set_xlabel('known lactose\nconcentration [mM]', fontsize=6)
ax[1].set_ylabel('integrated signal\nintensity' +
                 r' [$\times 10^6$ a.u.]', fontsize=6)
ax[2].set_ylim([-0.1, 5])
ax[2].set_yticks([0, 1, 2, 3, 4, 5])
ax[2].set_yticklabels([0, 1, 2, 3, 4, 5])
ax[2].set_xlabel('retention time [min]', fontsize=6)
ax[2].set_ylabel(r'signal intensity [$\times 10^4$ a.u.]', fontsize=6)

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

# Plot the representative buffer peak and it's fit.
ax[2].plot(buff_chrom.df['time'], buff_chrom.df[buff_chrom.int_col] /
           1E4, '-', lw=1.5, color=cor['purple'])
ax[2].fill_between(buff_chrom.df['time'], buff_chrom.df[buff_chrom.int_col] /
                   1E4, '-', lw=1.5, color=cor['pale_purple'])
ax[2].plot(buff_chrom.df['time'], buff_chrom.unmixed_chromatograms /
           1E4, '--', color=cor['primary_red'], lw=1.5)
plt.savefig('./figures/Fig3_cal_curve_panels.pdf', bbox_inches='tight')
# %%
# Get the peak parameters of the baseline peak
buffer_df = pd.DataFrame([])
for idx in range(1, 4):
    df = pd.read_csv(f'./data/buffer_{idx}.csv')
    base_chrom = Chromatogram(df, time_window=[12, 15])
    base_peaks = base_chrom.fit_peaks(
        integration_window=[12, 16], verbose=False)
    base_peaks['idx'] = idx
    buffer_df = pd.concat([buffer_df, base_peaks], sort=False)
buffer_df

# %%
constraints = {}
low, high = [0.99, 1.01]
for g, d in base_peaks.groupby('peak_id'):
    constraints[d['retention_time'].values[0]] = {
        'amplitude': [low * buffer_df['amplitude'].min(),
                      high * buffer_df['amplitude'].max()],
        'skew': [low * d['skew'].min(), high * d['skew'].max()],
        'scale': [low * d['scale'].min(), high * d['scale'].max()]}
constraints[13.56] = {}  # {'scale': 0.28 * epsilon, 'skew': 1.6 * epsilon}

# %%
# Load the test files
test_files = glob.glob('./data/buffer_lactose*.csv')

# Run the inference twice, once using only the retention times and once with
# bounded parameters
test_constrained = pd.DataFrame([])
test_loose = pd.DataFrame([])
mapper = {'lactose': {'retention_time': 13.56,
                      'slope': popt[0], 'intercept': popt[1], 'unit': 'mM'}}
for f in test_files:
    # Get known concentration
    c = float(f.split('_')[-1].split('.csv')[0])

    # Fit the mixture and compute the concentration
    df = pd.read_csv(f)
    chrom = Chromatogram(df, time_window=[12, 16])
    _ = chrom.fit_peaks(known_peaks=constraints, tolerance=1,
                        integration_window=[12, 16])
    constrained_peaks = chrom.map_peaks(mapper, loc_tolerance=0.5)
    _ = chrom.fit_peaks(known_peaks=list(constraints.keys()), tolerance=1,
                        integration_window=[12, 16])
    loose_peaks = chrom.map_peaks(mapper, loc_tolerance=0.5)

    # Add the known concentration
    constrained_peaks['known_conc'] = c
    loose_peaks['known_conc'] = c
    test_constrained = pd.concat(
        [test_constrained, constrained_peaks], sort=False)
    test_loose = pd.concat([test_loose, loose_peaks], sort=False)

# %%
# Plot the constrained and unconstrainted chromatogram for a mixture
mix = pd.read_csv('./data/buffer_lactose_mM_8.csv')
chrom = Chromatogram(mix, time_window=[12, 16])

fig, ax = plt.subplots(1, 2, figsize=(3.5, 0.75), sharex=True)
for a in ax:
    a.set_xlim([12, 15])
    a.tick_params(labelsize=6)
    a.spines['bottom'].set_visible(True)
    a.spines['bottom'].set_linewidth(0.2)
    a.spines['bottom'].set_color(cor['primary_black'])
    a.plot(chrom.df['time'], chrom.df[chrom.int_col]/1E4,
           '-', color=cor['primary_black'], lw=1.25)
    a.set_xlabel('retention time [min]', fontsize=6)
    a.set_ylabel('signal intensity\n'+r'[$\times 10^4$ a.u.]', fontsize=6)

constrained = chrom.fit_peaks(
    known_peaks=constraints, tolerance=0.5, integration_window=[12, 16])

ax[0].plot(chrom.df['time'], chrom.unmixed_chromatograms[:, 0]/1E4,
           color=cor['purple'], lw=0.5)
ax[0].fill_between(
    chrom.df['time'], chrom.unmixed_chromatograms[:, 0]/1E4, color=cor['pale_purple'], alpha=0.5)

ax[0].plot(chrom.df['time'], chrom.unmixed_chromatograms[:, 1]/1E4,
           color=cor['blue'], lw=0.5, zorder=10001)
ax[0].fill_between(
    chrom.df['time'], chrom.unmixed_chromatograms[:, 1]/1E4, color=cor['pale_blue'], zorder=1000, alpha=0.5)
ax[0].plot(chrom.df['time'], np.sum(chrom.unmixed_chromatograms, axis=1)/1E4, '--',
           color=cor['light_red'], lw=0.5, zorder=10001)


unconstrained = chrom.fit_peaks(
    known_peaks=list(constraints.keys()), tolerance=0.5, integration_window=[12, 16])

ax[1].plot(chrom.df['time'], chrom.unmixed_chromatograms[:, 1]/1E4,
           color=cor['blue'], lw=0.5, zorder=10001)
ax[1].fill_between(
    chrom.df['time'], chrom.unmixed_chromatograms[:, 1]/1E4, color=cor['pale_blue'], zorder=1000, alpha=0.5, hatch='....', edgecolor=cor['dark_blue'], linewidth=0.5)
ax[1].plot(chrom.df['time'], np.sum(chrom.unmixed_chromatograms, axis=1)/1E4, '--',
           color=cor['light_red'], lw=0.5, zorder=10001)
ax[1].plot(chrom.df['time'], chrom.unmixed_chromatograms[:, 0]/1E4,
           color=cor['purple'], lw=0.5, zorder=10001)
ax[1].fill_between(
    chrom.df['time'], chrom.unmixed_chromatograms[:, 0]/1E4, color=cor['pale_purple'], alpha=0.5, zorder=1000)

plt.savefig('./figures/Fig3_constrained_unconstrained_mixes.pdf',
            bbox_inches='tight')
# loose = chrom.fit_peaks(known_peaks=list(constraints.keys()))
# %%
fig, ax = plt.subplots(1, 2, figsize=(3.5, 1.5))
ax[1].set_ylim([0, 25])
ax[0].set_xlabel('known lactose\nconcentration [mM]', fontsize=6)
ax[0].set_ylabel('inferred lactose\nconcentration [mM]', fontsize=6)
ax[1].set_xlabel('known lactose\nconcentration [mM]', fontsize=6)
ax[1].set_ylabel('inferred lactose\nconcentration [mM]', fontsize=6)

ax[0].plot(test_constrained['known_conc'], test_constrained['concentration'], 'o', ms=8, color=cor['light_blue'],
           markeredgecolor=cor['dark_blue'])
for g, d in test_loose.groupby('known_conc'):
    ax[1].plot(d['known_conc'], d['concentration'], 'o', ms=8, color=cor['pale_blue'],
               markeredgecolor=cor['dark_blue'])
    ax[1].plot(d['known_conc'], d['concentration'], '.', ms=4, color=cor['dark_blue'],
               markeredgecolor=cor['dark_blue'])

ax[0].set_xticks([0, 3, 6, 9])
ax[1].set_xticks([0, 3, 6, 9])
ax[0].set_yticks([0, 3, 6, 9])
ax[1].set_yticks([0, 10, 20])

for a in ax:
    a.plot([0, 10], [0, 10], 'k--', lw=2)
    a.tick_params(labelsize=6)
plt.savefig('./figures/Fig3_validation.pdf', bbox_inches='tight')
# %%
