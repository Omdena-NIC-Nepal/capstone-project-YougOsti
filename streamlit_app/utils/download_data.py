import gdown
import os

def download_from_drive(file_id, output_path):
    url = f"https://drive.google.com/uc?id={file_id}"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    gdown.download(url, output_path, quiet=False)

def download_all_data():
    files = [
        {
            "file_id": "1WlyTmR7PNXsOsxcdBDfvYrugn3tfyT5f",
            "output": "Data/Raw/Environment_data/Landcover_2005_Icimod.tif"
        },
        {
            "file_id": "1h4U5HXM8BTWR1UHSBeapSf8zglxO-uGY",
            "output": "Data/Raw/Environment_data/Landcover_2010_Icimod.tif"
        },
        {
            "file_id": "1gcE3uEFuWJa2vANs_jDLw6_ciH_zThBO",
            "output": "Data/Raw/Environment_data/Landcover_2015_Icimod.tif"
        },
        {
            "file_id": "1NmzwIB5PE-GbViBu189mPu6jGGgumiza",
            "output": "Data/Raw/Environment_data/Glacier_cover_change.tif"
        },
        {
            "file_id": "1AQP2tKoxlIsu3FmQRyBvyrQVF6dRgo3_",
            "output": "Data/Raw/Environment_data/Glacier_area_by_HUCs.csv"
        }
    ]

    for item in files:
        print(f"Downloading to {item['output']}...")
        download_from_drive(item["file_id"], item["output"])
