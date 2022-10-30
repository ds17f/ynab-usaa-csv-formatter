# ynab-usaa-csv-formatter
USAA removed the ability to use OFX except through quicken.  This is terrible.
The only way to import transactions from USAA is by downloading a CSV.
That CSV needs to be reformatted for import into USAA.

USAA has a specific format for its import files.  
This script takes a USAA formatted CSV and converts it into a YNAB formatted CSV

The file will now be exported as OFX because YNAB will import that

## Installation
```
python -m venv .venv
. ./.venv/bin/activate
pip install -f requirements.txt
```

## Usage
The script is currently hard coded to look for `./sample.csv` as the input and `./output.csv` as the output.  It will also produce a `./output.ofx` file.

```bash
$> ls
sample.csv
main.py

$> python main.py

$> ls
sample.csv
output.csv
output.ofx
main.py
```

