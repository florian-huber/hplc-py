---
title: 'hplc-py: Rapid Quantification of Complex Chemical Chromatograms'
tags:
  - Python
  - Analytical Chemistry
  - Quantitative Methods
  - HPLC
  - Chromatography
authors:
  - name: Griffin Chure
    orcid: 0000-0000-0000-0000
    affiliation: 1
  - name: Jonas Cremer
    orcid: 
    affiliation: 1
affiliations:
 - name: Department of Biology, Stanford University, CA, USA
   index: 1
date: 01 October 2023
bibliography: paper.bib
---

# Summary

High Performance Liquid Chromatography (HPLC) has become a gold-standard method
across diverse fields for precise quantitation of aqueous mixtures and
chromatographic separation of the constituent chemical species. Technological
advancements in sample preparation and mechanical automation have allowed HPLC
to become a high-throughput tool which poses new challenges for reproducible and
rapid analysis of the resulting chromatograms. Here we present `hplc-py`, a
Python package that permits rapid and reliable quantitation of component signals
within a chromatographic spectrum for pipelined workflows.  This package is
particularly effective at deconvolving highly overlapping signals, allowing for
precise absolute quantitation of chemical constituents with similar
chromatographic retention times.

# Statement of Need 
High-Performance Liquid Chromatography (HPLC) is an analytical technique which
allows for the quantitative characterization of the chemical components of
aqueous mixtures. Of particular interest is the integrated signal While many of
the technical details of HPLC are now automated, the programmatic cleaning and
processing of the resulting data can be cumbersome. Open-source tools such as `HappyTools` [@jansen2018]

Modern tools for quantitative processing of chromatographic spectra often require
manual curation of

# Methodology 

# Experimental Validation With Highly Overlapping Lactose-Phosphate Signals

# Data & Code Availability
All experimental data and code used to process data schematized in Figure 1 and 2 
are publicly available on the [`hplc-py` GitHub repository `publication` branch](https://github.com/cremerlab/hplc-py/tree/publication).

# Acknowledgements 
We thank Markus Arnoldini and Richa Sharma for extensive discussion of software
needs and for prototyping early releases and Olivia Warren for advice in
software design and implementation. We also thank Richa Sharma for collection of
the overlapping signal data used in Figure 2 to experimentally validate the
software.  Griffin Chure acknowledges financial support by the NSF Postdoctoral 
Research Fellowships in Biology Program (grant no. 2010807).

# References