# (optional) create virutalenv
```
python -m venv my_livedata_env
source my_livedata_env/activate
python --version
which python
which pip
```
# Install requirements
`pip install -r requirements.txt`

# Start the script that collects data in background

` python livedata.py <PATH TO DATABASE> `
the database is created if it does not exist.

# Plot the live data
` python animate.py <PATH TO DATABASE> <LOOKBACK MINUTES> `

![Figure_1](https://user-images.githubusercontent.com/12353864/155135159-b9b38c94-2c77-42d2-b579-0e180a622fc6.png)
