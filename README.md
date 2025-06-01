# 🌍 Climate Change Impact Assessment and Prediction System for Nepal

This interactive dashboard provides data-driven insights on how climate change is affecting Nepal’s environment, agriculture, and biodiversity. It supports policymakers, researchers, and local communities by enabling analysis, forecasting, and visualization of climate variables and their impacts.


## Features

- Temperature and precipitation trend analysis (daily to yearly)
- Extreme weather detection and mapping
- Glacier retreat visualization and analysis
- Threatened species trend analysis
- Landcover change detection (from satellite raster data)
- Agricultural production trend and crop yield forecasting
- Correlation between climate and crop yield
- NLP analysis of climate-related news (sentiment, keywords, word cloud)
- Impact of extreme weather on glacier loss



## Folder Structure
capstone-project-YougOsti/
├── streamlit_app/
│ ├── app.py
│ └── utils/
│ ├── preprocess.py
│ ├── eda_plot.py
│ ├── agriculture.py
│ ├── biodiversity.py
│ ├── glacier.py
│ ├── landcover.py
│ ├── nlp_tools.py
│ └── glacier_weather_corr.py
├── Data/
│ ├── Raw/
│ │ ├── Weather&Climate_data/
│ │ ├── Environment_data/
    ├── Socioeconomic_data/
│ └── Processed/
├── processed/
│ ├── cleaned_dailyclimate.csv
│ ├── cleaned_agricultural_data.csv
│ └── threatened_species_cleaned.csv
├── requirements.txt
└── README.md


---

## Data Sources

- **Climate Data**: Department of Hydrology and Meteorology (DHM), Nepal  
- **Landcover and Glacier Data**: ICIMOD  
- **Agriculture Data**: Ministry of Agriculture and Livestock Development  
- **Threatened Species**: National Statistics Office (NSO), Nepal  
- **NLP Sample**: ReliefWeb – [Climate Crisis is a Water Crisis (Nepal)](https://reliefweb.int/report/nepal/climate-crisis-water-crisis)

Data Download:
Raw data can be downloaded from 'Raw' folder and cleaned data can be downloaded from 'processed' folder.

App Link : https://omdenanic-first-proj-voq7ev3gd9cm3qvuz62kdk.streamlit.app/