# Extended Essay Repository
## This repository contains the source code and datasets used for my Extended Essay project. The code involves web scraping from CodeForces and extracting features. 

## External Data
The original data used in this project is from the CodeComplex-Data repository. To respect licensing, the raw jsonl files are not included in this repository. In order to replicate this study, the original files must be downloaded from the CodeComplex repository and added to the data folder. 

## How to Use

1. Clone the repository
2. Install dependencies: pandas, beautifulsoup4, playwright, and pylatexenc.
3. Run DataMerger: Execute DataMerger.py to preprocess the JSONL data from the CodeComplex repository.
4. Run Extraction: Execute BuildDataset.py to process the merged JSONL data into the final CSV format.
