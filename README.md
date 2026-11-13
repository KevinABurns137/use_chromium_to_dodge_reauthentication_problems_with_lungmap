# use_chromium_to_dodge_reauthentication_problems_with_lungmap
it's all in the name


# Setup
python -m venv .spstatevenv       
.\.spstatevenv\Scripts\Activate.ps1    
pip install pathlib playwright    
playwright install chromium

# Reuse
it's a bespoke script to read the example spreadsheet, compose urls then export them to json. You'll have to do the configuring yourself

# command line 
python .\lungmap_sp_state_scraper.py   

# Safety
make sure you have a .gitignore with sp_storage_state.json in it, it contains your session and should not be shared
