# Calibration and Validation Data

## Method
All data in this folder, save for `sample.txt`, were collected on a [Shimadzu Prominence-i LC-2030C 3D Plus](https://www.gmi-inc.com/product/shimadzu-prominence-i-lc-2030c-3d-plus/)  High Performance Liquid Chromatography (HPLC). instrument outfitted
with a [Rezex ROA-Organic Acid H+ (8%) Ion Exclusion Column](https://www.phenomenex.com/products/rezex-hplc-column/rezex-roa-organic-acid-h)(300 x 7.8 mm) held 
at 40 °C. All samples were collected using a 10 µL injection volume and a 2.5 mM Sulfuric Acid isocratic mobile phase
with a flow rate of 400 µL / min. Measurements were collected using a [Shimadzu RID-20A](https://www.shimadzu.com/an/products/liquid-chromatography/hplc-components-accessories/rid-20a/index.html)
refractive index detector. All samples (save for `sample.txt` and `sample_chromatogram.txt`) 
were collected on a single observing run using an autosampler system. Each sample was
analyzed for 45 min to ensure complete run-through of analytes with low mobility. After 
collection, chromatograms were programmatically trimmed to the time window of interest 
for the data presentation in this work (between 12 and 17 min.).


The data files and their composition and listed below. 

| **Filename** | **Analyte(s) Present [Concentration]** |  **Notes**|
|:--:|:--:|:--:|
|`buffer_1.csv`| Inorganic Phosphate [112 mM]| Sample buffer prep #1|
|`buffer_2.csv`| Inorganic Phosphate [112 mM]| Sample buffer prep #2|
|`buffer_3.csv`| Inorganic Phosphate [112 mM]| Sample buffer prep #3|
|`lactose_mM_0.5.csv`| Lactose [0.5 mM]| Lactose aqueous solution|
|`lactose_mM_1.csv`| Lactose [1 mM]| Lactose aqueous solution|
|`lactose_mM_1.5.csv`| Lactose [1.5 mM]| Lactose aqueous solution|
|`lactose_mM_2.csv`| Lactose [2 mM]| Lactose aqueous solution|
|`lactose_mM_3.csv`| Lactose [3 mM]| Lactose aqueous solution|
|`lactose_mM_4.csv`| Lactose [4 mM]| Lactose aqueous solution|
|`lactose_mM_6.csv`| Lactose [6 mM]| Lactose aqueous solution|
|`lactose_mM_8.csv`| Lactose [8 mM]| Lactose aqueous solution|
|`buffer_lactose_mM_0.5.csv`| Inorganic Phosphate [112 mM] Lactose [0.5 mM]| Lactose-buffer mix|
|`buffer_lactose_mM_1.csv`  | Inorganic Phosphate [112 mM] Lactose [1 mM]  | Lactose-buffer mix|
|`buffer_lactose_mM_1.5.csv`| Inorganic Phosphate [112 mM] Lactose [1.5 mM]| Lactose-buffer mix|
|`buffer_lactose_mM_2.csv`  | Inorganic Phosphate [112 mM] Lactose [2 mM]  | Lactose-buffer mix|
|`buffer_lactose_mM_3.csv`  | Inorganic Phosphate [112 mM] Lactose [3 mM]  | Lactose-buffer mix|
|`buffer_lactose_mM_4.csv`  | Inorganic Phosphate [112 mM] Lactose [4 mM]  | Lactose-buffer mix|
|`buffer_lactose_mM_6.csv`  | Inorganic Phosphate [112 mM] Lactose [6 mM]  | Lactose-buffer mix|
|`buffer_lactose_mM_8.csv`  | Inorganic Phosphate [112 mM] Lactose [8 mM]  | Lactose-buffer mix|



The data files listed above were used in making a lactose calibration curve 
(as shown in Fig. 2D-E of the associated paper) and in deconvolving a phosphate-lactose 
mixture (Fig. 3). While only phosphate is present in the chromatograms, the source 
comes from a more complex buffer (N-C- Minimal Medium) with the following composition.

| **Chemical Species** | **Final Concentration [mM]** | 
|:--:|:--:|
|K<sub>2</sub>SO<sub>4</sub> | 5.7 | 
|K<sub>2</sub>HPO<sub>4</sub> | 77.5|
|KH<sub>2</sub>PO<sub>4</sub> | 34.5|
|MgSO<sub>4</sub> | 0.4|
|NaCl | 43.1 |

An example of a complete chromatogram of this buffer (+ 10mM NH<sub>4</sub>Cl + 10mM glucose) is
given as `sample_chromatogram.txt`  and was used for panels A - C of Figure 2. The file `sample.txt` 
is the simulated chromatogram shown in Figure 1. 
