from typing import List
from csv import reader, writer
from collections import namedtuple
from csv2ofx import utils
from csv2ofx.ofx import OFX
from csv2ofx.mappings.default import mapping
from operator import itemgetter
import itertools as it
from meza.io import read_csv, IterStringIO

import logging
LOGGER = logging.getLogger(__name__)

USAA_ROW_FIELDS = [
    "Date", "Description", "OriginalDescription", "Category", "Amount", "Status"
]
YNAB_ROW_FIELDS = [
    "Date", "Payee" , "Category" , "Memo" , "Outflow" , "Inflow"
]
USAA_ROW = namedtuple('USAA_ROW', USAA_ROW_FIELDS)
YNAB_ROW = namedtuple('YNAB_ROW', YNAB_ROW_FIELDS)

USAA_MAPPING = {
    'bank': 'USAA',
    'account': 'Joint Checking',
    'date': itemgetter('Date'),
    'amount': itemgetter('Amount'),
    'payee': itemgetter('Description'),
    'notes': itemgetter('Memo')
}

def _read_file(csv_filename: str, skip_rows: int = 0) -> List[USAA_ROW]:
    """Reads the rows of the CSV file and returns a list of those rows"""
    skipped_rows = 0
    rows = []
    LOGGER.info("reading rows from file")
    with open(csv_filename, newline="") as csvfile:
        csv_reader = reader(csvfile)
        for row in csv_reader:
            LOGGER.debug(f"raw row: {row}")

            if not row:
                LOGGER.debug("skipping blank row")
                continue

            if skip_rows > skipped_rows:
                LOGGER.info(f"skipping row: {skipped_rows + 1}")
                skipped_rows += 1
                continue

            usaa_row = USAA_ROW(*row)
            LOGGER.debug(f"USAA Row: {usaa_row}")
            rows.append(usaa_row)

    LOGGER.info(f"Found {len(rows)} rows.")
    return rows

def _transform_usaa_to_ynab(usaa_data: List[USAA_ROW]) -> List[YNAB_ROW]:
    """Takes in USAA data and turns it into YNAB data"""
    LOGGER.info("Transforming USAA data into YNAB data")
    ynab_rows = []
    for usaa_row in usaa_data:
        LOGGER.debug(f"USAA ROW: {usaa_row}")
        try:
            ynab_row = YNAB_ROW(
                Date=usaa_row.Date,
                Payee=usaa_row.Description,
                Category="",
                Memo="",
                Outflow="",
                Inflow=float(usaa_row.Amount.replace("--", "")),
            )
        except Exception as e:
            LOGGER.error(f"Error '{e}' when parsing USAA ROW: [{usaa_row}]")
            raise e
        LOGGER.debug(f"YNAB ROW: {ynab_row}")
        ynab_rows.append(ynab_row)

    LOGGER.info(f"Transformed {len(ynab_rows)} rows")
    return ynab_rows

def _transform_ynab_csv_to_ofx(ynab_csv_filename: str):
    LOGGER.info("Transforming YNAB CSV to QFX")
    ofx = OFX(USAA_MAPPING)
    records = read_csv(ynab_csv_filename, has_header=True)
    # records = [dict(yd) for yd in ynab_data]
    #records = [yd._asdict for yd in ynab_data]
    LOGGER.debug(f"YNAB csv as QFX records: {records}")
    groups = ofx.gen_groups(records)
    trxns = ofx.gen_trxns(groups)
    cleaned_trxns = ofx.clean_trxns(trxns)
    data = utils.gen_data(cleaned_trxns)
    content = it.chain([ofx.header(), ofx.gen_body(data), ofx.footer()])
    output = ""
    for line in IterStringIO(content):
        print(line.decode("utf-8"))
        output += line.decode("utf-8")
    return output

def _write_ynab_file_out(ynab_data: List[YNAB_ROW], file_path: str) -> str:
    """Writes the file to a temp location and returns the filename"""
    temp_file = file_path #"./TMP_FILE.csv" #TODO: use a legit python temp file
    with open(temp_file, 'w', newline='') as csvfile:
        csv_writer = writer(csvfile)
        # write the headers
        csv_writer.writerow(YNAB_ROW_FIELDS)
        # write the data
        for ynab_row in ynab_data:
            csv_writer.writerow(ynab_row)

    return temp_file

def _write_ofx_file(ofx_data, file_name: str):
    with open(file_name, 'w') as f:
        f.write(ofx_data)

def _open_ynab_for_import(file_path: str) -> None:
    pass

def main(input_filename: str, output_filename: str) -> None:
    """ Processes the input_file USAA csv file into a YNAB friendly file

    :param input_filename: The USAA formatted file to read in
    :param output_filename: The YNAB formatted file to write out
    """
    LOGGER.info(f"processing file: {input_filename}")
    usaa_data = _read_file(input_filename, 1)
    ynab_data = _transform_usaa_to_ynab(usaa_data)
    output_filename = _write_ynab_file_out(ynab_data, file_path=output_filename)

    ofx_data = _transform_ynab_csv_to_ofx(input_filename)
    _write_ofx_file(ofx_data, "output.ofx")

    _open_ynab_for_import(output_filename)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.handlers.append(logging.StreamHandler())

    LOGGER.debug("running from __main__")
    main("./sample.csv", "./output.csv")

