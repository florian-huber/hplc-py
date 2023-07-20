import pandas as pd 
import numpy as np
import scipy.signal
import scipy.optimize
import scipy.special
import tqdm
import matplotlib.pyplot as plt
import seaborn as sns


class Chromatogram(object):
    """
    Base class for the processing and quantification of HPLC chromatograms
    """
    def __init__(self, file=None, time_window=None,
                    bg_subtract=True,
                    peak_width=3,
                    cols={'time':'time_min', 'intensity':'intensity_mV'},
                    csv_comment='#'):
        """
        Instantiates a chromatogram object on which peak detection and quantification
        is performed.

        Parameters
        ----------
        file: str or pandas DataFrame, optional
            The path to the csv file of the chromatogram to analyze or 
            the pandas DataFrame of the chromatogram. If None, a pandas DataFrame 
            of the chromatogram must be passed.
        dataframe : pandas DataFrame, optional
            a Pandas Dataframe of the chromatogram to analyze. If None, 
            a path to the csv file must be passed
        time_window: list [start, end], optional
            The retention time window of the chromatogram to consider for analysis.
            If None, the entire time range of the chromatogram will be considered.
        bg_subtract: bool, optional
            If True, sensitive nonlinear iterative peak (SNIP) clipping is used 
            to estimate and subtract the signal baseline.
        peak_width: float, optional
            The approximate full-width half-maximum (FWHM) of the peaks of interest. 
            This is used to set the number of iterations needed for the background
            subtraction.
        cols: dict, keys of 'time', and 'intensity', optional
            A dictionary of the retention time and intensity measurements 
            of the chromatogram. Default is 
            `{'time':'time_min', 'intensity':'intensity_mV'}`.
        csv_comment: str, optional
            Comment delimiter in the csv file if chromatogram is being read 
            from disk.
        """

        # Peform type checks and throw exceptions where necessary. 
        if file is None:
            raise RuntimeError(f'File path or dataframe must be provided')
        if (type(file) is not str) & (type(file) is not pd.core.frame.DataFrame):
            raise RuntimeError(f'Argument must be either a filepath or pandas DataFrame. Argument is of type {type(file)}')
        if (time_window is not None):
            if type(time_window) != list:
                raise TypeError(f'`time_window` must be of type `list`. Type {type(time_window)} was proivided')
            if len(time_window) != 2:
                raise ValueError(f'`time_window` must be of length 2 (corresponding to start and end points). Provided list is of length {len(time_window)}.')

        # Assign class variables 
        self.time_col = cols['time']
        self.int_col = cols['intensity']

        # Load the chromatogram and necessary components to self. 
        if type(file) is str:
            dataframe = pd.read_csv(file, comment='#')
        else:
            dataframe = file 
        self.df = dataframe

        # Prune to time window
        if time_window is not None:
            self.crop(time_window)
        else: 
            self.df = dataframe

        # Correct for a negative baseline 
        if bg_subtract:
            self._bg_subtract(window=peak_width)

        # Blank out vars that are used elsewhere
        self.window_df = None
        self.window_props = None
        self.peaks = None
        self.peak_df = None

    def crop(self, time_window=None, return_df=False):
        """
        Restricts the time dimension of the DataFrame

        Parameters
        ----------
        time_window : list [start, end], optional
            The retention time window of the chromatogram to consider for analysis.
            If None, the entire time range of the chromatogram will be considered.
        return_df : bool
            If `True`, the cropped DataFrame is 

        Returns
        -------
        cropped_df : pandas DataFrame
            If `return_df = True`, then the cropped dataframe is returned.
        """
        if type(time_window) != list:
                raise TypeError(f'`time_window` must be of type `list`. Type {type(time_window)} was proivided')
        if len(time_window) != 2:
                raise ValueError(f'`time_window` must be of length 2 (corresponding to start and end points). Provided list is of length {len(time_window)}.')
        self.df = self.df[(self.df[self.time_col] >= time_window[0]) & 
                          (self.df[self.time_col] <= time_window[1])]
        if return_df:
            return self.df

    def _assign_peak_windows(self, prominence=0.01, rel_height=0.95, buffer=100):
        """
        Breaks the provided chromatogram down to windows of likely peaks. 

        Parameters
        ----------
        prominence : float,  [0, 1]
            The promimence threshold for identifying peaks. Prominence is the 
            relative height of the normalized signal relative to the local
            background. Default is 1%.
        rel_height : float, [0, 1]
            The relative height of the peak where the baseline is determined. 
            Default is 95%.
        buffer : positive int
            The padding of peak windows in units of number of time steps. Default 
            is 100 points on each side of the identified peak window.

        Returns
        -------
        windows : pandas DataFrame
            A Pandas DataFrame with each measurement assigned to an identified 
            peak or overlapping peak set. This returns a copy of the chromatogram
            DataFrame with  a column  for the local baseline and one column for 
            the window IDs. Window ID of -1 corresponds to area not assigned to 
            any peaks
        """
        for param, param_name, param_type in zip([prominence, rel_height, buffer], 
                                     ['prominence', 'rel_height',  'buffer'],
                                     [float, float, int]):
            if type(param) is not param_type:
                raise TypeError(f'Parameter {param_name} must be of type `{param_type}`. Type `{type(param)}` was supplied.') 
        if (prominence < 0) | (prominence > 1):
            raise ValueError(f'Parameter `prominence` must be [0, 1].')
        if (rel_height < 0) | (rel_height > 1):  
            raise ValueError(f'Parameter `rel_height` must be [0, 1].')
        if (buffer < 0):
            raise ValueError('Parameter `buffer` cannot be less than 0.')

        # Correct for a negative baseline 
        df = self.df
        intensity = self.df[self.int_col].values
        norm_int = (intensity - intensity.min()) / (intensity.max() - intensity.min())

        # Identify the peaks and get the widths and baselines
        peaks, _ = scipy.signal.find_peaks(norm_int, prominence=prominence)
        self.peaks_inds = peaks
        out = scipy.signal.peak_widths(intensity, peaks, 
                                       rel_height=rel_height)
        _, heights, left, right = out
        widths, _, _, _ = scipy.signal.peak_widths(intensity, peaks, 
                                       rel_height=0.5)

        # Set up the ranges
        ranges = []
        for l, r in zip(left, right):
            if (l - buffer) < 0:
                l = 0
            else:
                l -= buffer
            if (r + buffer) > len(norm_int):
                r = len(norm_int)
            else:
                r += buffer
            ranges.append(np.arange(np.round(l), np.round(r), 1))

        # Identiy subset ranges and remove
        valid = [True] * len(ranges)
        for i, r1 in enumerate(ranges):
            for j, r2 in enumerate(ranges):
                if i != j:
                    if set(r2).issubset(r1):
                        valid[j] = False
        
        # Keep only valid ranges and baselines
        ranges = [r for i, r in enumerate(ranges) if valid[i] is True]
        baselines = [h for i, h in enumerate(heights) if valid[i] is True]

        # Copy the dataframe and return the windows
        window_df = df.copy(deep=True)
        window_df.sort_values(by=self.time_col, inplace=True)
        window_df['time_idx'] = np.arange(len(window_df))
        for i, r in enumerate(ranges):
            window_df.loc[window_df['time_idx'].isin(r), 
                                    'window_idx'] = int(i + 1)
            window_df.loc[window_df['time_idx'].isin(r), 
                                    'baseline'] = baselines[i]
        window_df.dropna(inplace=True) 

        # Convert this to a dictionary for easy parsing
        window_dict = {}
        time_step = np.mean(np.diff(self.df[self.time_col].values))
        for g, d in window_df.groupby('window_idx'):
            _peaks = [p for p in peaks if p in d['time_idx'].values]
            peak_inds = [x for _p in _peaks for x in np.where(peaks == _p)[0]]
            _dict = {'time_range':d[self.time_col].values,
                     'intensity': d[self.int_col] - baselines[i],
                     'num_peaks': len(_peaks),
                     'amplitude': [d[d['time_idx']==p][self.int_col].values[0] - baselines[i] for p in _peaks],
                     'location' : [d[d['time_idx']==p][self.time_col].values[0] for p in _peaks],
                     'width' :    [widths[ind] * time_step for ind in peak_inds]
                     }
            window_dict[g] = _dict
        self.window_props = window_dict
        return window_df  

    def _compute_skewnorm(self, x, *params):
        R"""
        Computes the lineshape of a skew-normal distribution given the shape,
        location, and scale parameters

        Parameters
        ----------
        x : float or numpy array
            The time dimension of the skewnorm 
        params : list, [amplitude, loc, scale, alpha]
            Parameters for the shape and scale parameters of the skewnorm 
            distribution.
                amplitude : float; > 0
                    Height of the peak.
                loc : float; > 0
                    The location parameter of the distribution.
                scale : float; > 0
                    The scale parameter of the distribution.
                alpha : float; > 
                    THe skew shape parater of the distribution.

        Returns
        -------
        scaled_pdf : float or numpy array, same shape as `x`
            The PDF of the skew-normal distribution scaled with the supplied 
            amplitude.

        Notes
        -----
        This function infers the parameters defining skew-norma distributions 
        for each peak in the chromatogram. The fitted distribution has the form 
            
        .. math:: 
            I = 2I_\text{max} \left(\frac{1}{\sqrt{2\pi\sigma^2}}\right)e^{-\frac{(t - r_t)^2}{2\sigma^2}}\left[1 + \text{erf}\frac{\alpha(t - r_t)}{\sqrt{2\sigma^2}}\right]

        where :math:`I_\text{max}` is the maximum intensity of the peak, 
        :math:`t` is the time, :math:`r_t` is the retention time, :math:`\sigma`
        is the scale parameter, and :math:`\alpha` is the skew parameter.

        """
        amp, loc, scale, alpha = params
        _x = alpha * (x - loc) / scale
        norm = np.sqrt(2 * np.pi * scale**2)**-1 * np.exp(-(x - loc)**2 / (2 * scale**2))
        cdf = 0.5 * (1 + scipy.special.erf(_x / np.sqrt(2))) 
        return amp * 2 * norm * cdf

    def _fit_skewnorms(self, x, *params):
        R"""
        Estimates the parameters of the distributions which consititute the 
        peaks in the chromatogram. 

        Parameters
        ----------
        x : float
            The time dimension of the skewnorm 
        params : list of length 4 x number of peaks, [amplitude, loc, scale, alpha]
            Parameters for the shape and scale parameters of the skewnorm 
            distribution. Must be provided in following order, repeating
            for each distribution.
                amplitude : float; > 0
                    Height of the peak.
                loc : float; > 0
                    The location parameter of the distribution.
                scale : float; > 0
                    The scale parameter of the distribution.
                alpha : float; > 
                    THe skew shape parater of the distribution.

        Returns
        -------
        out : float
            The evaluated distribution at the given time x. This is the summed
            value for all distributions modeled to construct the peak in the 
            chromatogram.
        """
        # Get the number of peaks and reshape for easy indexing
        n_peaks = int(len(params) / 4)
        params = np.reshape(params, (n_peaks, 4))
        out = 0
        
        # Evaluate each distribution
        for i in range(n_peaks):
            out += self._compute_skewnorm(x, *params[i])
        return out
        
    def _estimate_peak_params(self, verbose=True):
        R"""
        For each peak window, estimate the parameters of skew-normal distributions 
        which makeup the peak(s) in the window.  

        Parameters
        ----------
        verbose : bool
            If `True`, a progress bar will be printed during the inference.
        """ 
        if self.window_props is None:
            raise RuntimeError('Function `_assign_peak_windows` must be run first. Go do that.')
        if verbose:
            iterator = tqdm.tqdm(self.window_props.items(), desc='Fitting peak windows...')  
        else:
            iterator = self.window_props.items()

        peak_props = {}
        for k, v in iterator:
            window_dict = {}
            # Set up the initial guess
            p0 = [] 
            bounds = [[],  []] 
            for i in range(v['num_peaks']):
                p0.append(v['amplitude'][i])
                p0.append(v['location'][i]),
                p0.append(v['width'][i] / 2) # scale parameter
                p0.append(0) # Skew parameter, starts with assuming Gaussian

                # Set the bounds 
                bounds[0].append(0)
                bounds[0].append(v['time_range'].min())
                bounds[0].append(0)
                bounds[0].append(-np.inf)
                bounds[1].append(np.inf)
                bounds[1].append(v['time_range'].max())
                bounds[1].append(np.inf)
                bounds[1].append(np.inf)

            # Perform the inference
            try:
                popt, _ = scipy.optimize.curve_fit(self._fit_skewnorms, v['time_range'],
                                               v['intensity'], p0=p0, bounds=bounds,
                                               maxfev=int(1E4))

                # Assemble the dictionary of output 
                if v['num_peaks'] > 1:
                    popt = np.reshape(popt, (v['num_peaks'], 4)) 
                else:
                    popt = [popt]
                for i, p in enumerate(popt):
                    window_dict[f'peak_{i + 1}'] = {
                                'amplitude': p[0],
                                'retention_time': p[1],
                                'std_dev': p[2],
                                'alpha': p[3],
                                'area':self._compute_skewnorm(v['time_range'], *p).sum()}
                peak_props[k] = window_dict
            except RuntimeError:
                print('Warning: Parameters could not be inferred for one peak')
        self.peak_props = peak_props
        return peak_props

    def quantify(self, time_window=None, prominence=1E-2, rel_height=1.0, 
                 buffer=100, verbose=True, **kwargs):
        R"""
        Quantifies peaks present in the chromatogram

        Parameters
        ----------
        time_window: list [start, end], optional
            The retention time window of the chromatogram to consider for analysis.
            If None, the entire time range of the chromatogram will be considered.
        prominence : float,  [0, 1]
            The promimence threshold for identifying peaks. Prominence is the 
            relative height of the normalized signal relative to the local
            background. Default is 1%.
        rel_height : float, [0, 1]
            The relative height of the peak where the baseline is determined. 
            Default is 95%.
        buffer : positive int
            The padding of peak windows in units of number of time steps. Default 
            is 100 points on each side of the identified peak window. 
        verbose : bool
            If True, a progress bar will be printed during the inference. 

        Returns
        -------
        peak_df : pandas DataFrame
            A dataframe containing information for each detected peak.


        Notes
        -----
        This function infers the parameters defining skew-norma distributions 
        for each peak in the chromatogram. The fitted distribution has the form 
            
        .. math:: 
            I = 2I_\text{max} \left(\frac{1}{\sqrt{2\pi\sigma^2}}\right)e^{-\frac{(t - r_t)^2}{2\sigma^2}}\left[1 + \text{erf}\frac{\alpha(t - r_t)}{\sqrt{2\sigma^2}}\right]

        where :math:`I_\text{max}` is the maximum intensity of the peak, 
        :math:`t` is the time, :math:`r_t` is the retention time, :math:`\sigma`
        is the scale parameter, and :math:`\alpha` is the skew parameter.

        """
        if time_window is not None:
            dataframe = self.df
            self.df = dataframe[(dataframe[self.time_col] >= time_window[0]) & 
                              (dataframe[self.time_col] <= time_window[1])].copy(deep=True) 
        # Assign the window bounds
        _ = self._assign_peak_windows(prominence, rel_height, buffer)

        # Infer the distributions for the peaks
        peak_props = self._estimate_peak_params(verbose)

        # Set up a dataframe of the peak properties
        peak_df = pd.DataFrame([])
        iter = 0 
        for _, peaks in peak_props.items():
            for _, params in peaks.items():
                _dict = {'retention_time': params['retention_time'],
                         'scale': params['std_dev'],
                         'skew': params['alpha'],
                         'amplitude': params['amplitude'],
                         'area': params['area'],
                         'peak_idx': iter + 1}     
                iter += 1
                peak_df = pd.concat([peak_df, pd.DataFrame(_dict, index=[0])])
                peak_df['peak_idx'] = peak_df['peak_idx'].astype(int)
        self.peak_df = peak_df

        # Compute the mixture
        time = self.df[self.time_col].values
        out = np.zeros((len(time), len(peak_df)))
        iter = 0
        for _ , _v in self.peak_props.items():
            for _, v in _v.items():
                params = [v['amplitude'], v['retention_time'], 
                          v['std_dev'], v['alpha']]
                out[:, iter] = self._compute_skewnorm(time, *params)
                iter += 1
        self.mix_array = out
        return peak_df
    
    def _bg_subtract(self, window=3, return_df=False):
        R"""
        Performs Sensitive Nonlinear Iterative Peak (SNIP) clipping to estimate 
        and subtract background in chromatogram.

        Parameters
        ----------
        window : int
            The approximate size of signal objects in the chromatogram in dimensions
            of time. This is related to the number of iterations undertaken by 
            the SNIP algorithm.
        return_df : bool
            If `True`, then chromatograms (before and after background correction) are returned

        Returns
        -------
        corrected_df : pandas DataFrame
            If `return_df = True`, then the original and the corrected chromatogram are returned.

        Notes
        -----
        This implements the SNIP algorithm as presented and summarized in `Morhác
        and Matousek 2008 <https://doi.org/10.1366/000370208783412762>`_.
        """

        # Unpack and copy dataframe and intensity profile
        df = self.df
        signal = df[self.int_col].copy()

        # Ensure positivity of signal
        signal *= np.heaviside(signal, 0)

        # Compute the LLS operator
        tform = np.log(np.log(np.sqrt(signal + 1) + 1) + 1)

        # Compute the number of iterations given the window size.
        dt = np.mean(np.diff(df[self.time_col].values))
        iter = int(((window / dt) - 1) / 2)

        # Iteratively filter the signal
        for i in range(0,iter):
            tform_new = tform.copy()
            for j in range(i, len(tform) - i):
                tform_new[j] = min(tform_new[j], 0.5 * (tform_new[j+i] + tform_new[j-i])) 
            tform = tform_new

        # Perform the inverse of the LLS transformation
        inv_tform = (np.exp(np.exp(tform) - 1) - 1)**2 - 1 

        # Add a new column to the dataframe which contains the background 
        # subtracted intensity and update the intensity column name in the 
        # object.
        df[self.int_col] = signal - inv_tform
        df[f'estimated_background'] = inv_tform 
        self.df = df  
        if return_df:
            return df

    def show(self):
        """
        Displays the chromatogram with mapped peaks if available.
        """
        sns.set()

        # Set up the figure    
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        ax.set_xlabel(self.time_col)
        ax.set_ylabel(self.int_col)

        # Plot the raw chromatogram
        print(self.int_col)
        ax.plot(self.df[self.time_col], self.df[self.int_col], 'k-', lw=2,
                label='raw chromatogram') 

        # Compute the skewnorm mix 
        if self.peak_df is not None:
            time = self.df[self.time_col].values
            # Plot the mix
            convolved = np.sum(self.mix_array, axis=1)

            ax.plot(time, convolved, 'r--', label='inferred mixture') 
            for i in range(len(self.peak_df)):
                ax.fill_between(time, self.mix_array[:, i], label=f'peak {i+1}', 
                                alpha=0.5)
        ax.legend(bbox_to_anchor=(1,1))
        fig.patch.set_facecolor((0, 0, 0, 0))
        return [fig, ax]