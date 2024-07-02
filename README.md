# Installation
1) Clone the repo
`git clone XX`
2) Cd into cloned dir
`cd XX`
3) Setup env
`conda env create -f "env.yml"`
4) Enable execution file mode on parse.py
`chmod +x parse.py`


# Usage
1) Call the parser with the statement(s) exported from Synchrony's website
`./parse <path/to/statement1.pdf> <path/to/statement2.pdf>  ...`

2) Resulting CSV files are written per file to the same as the input path but as .csv:
`<path/to/statement1.csv>`
`<path/to/statement2.csv>`