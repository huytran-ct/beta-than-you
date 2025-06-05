# Prerequisites 
Install depencies by uv
```code
uv pip install
```
# Download Data
download the ad-info, ad-performance and orders from `https://console.cloud.google.com/storage/browser/ct-ai-temp/hackathon` and put them to data/ folder

# Create the database
Run script
```code
python -m scripts.write_dataframe_to_sqlite
```