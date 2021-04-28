from typing import List
from csv import reader, writer
from collections import namedtuple
import logging
LOGGER = logging.getLogger(__name__)

USAA_ROW_FIELDS = [
    "cleared", "blank", "date", "blank1", "memo", "category", "amount"
]
YNAB_ROW_FIELDS = [
    "Date", "Payee" , "Category" , "Memo" , "Outflow" , "Inflow"
]
USAA_ROW = namedtuple('USAA_ROW', USAA_ROW_FIELDS)
YNAB_ROW = namedtuple('YNAB_ROW', YNAB_ROW_FIELDS)

def _read_file(csv_filename: str) -> List[USAA_ROW]:
    """Reads the rows of the CSV file and returns a list of those rows"""
    rows = []
    LOGGER.info("reading rows from file")
    with open(csv_filename, newline="") as csvfile:
        csv_reader = reader(csvfile)
        for row in csv_reader:
            LOGGER.debug(f"raw row: {row}")
            if not row:
                LOGGER.debug("skipping blank row")
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
        ynab_row = YNAB_ROW(
            Date=usaa_row.date,
            Payee=usaa_row.memo,
            Category="",
            Memo="",
            Outflow="",
            Inflow=float(usaa_row.amount),
        )
        LOGGER.debug(f"YNAB ROW: {ynab_row}")
        ynab_rows.append(ynab_row)

    LOGGER.info(f"Transformed {len(ynab_rows)} rows")
    return ynab_rows


def _write_ynab_file_out(ynab_data: List[YNAB_ROW], file_path: str) -> str:
    """Writes the file to a temp location and returns the filename"""
    temp_file = "./TMP_FILE.csv" #TODO: use a legit python temp file
    with open(temp_file, 'w', newline='') as csvfile:
        csv_writer = writer(csvfile)
        # write the headers
        csv_writer.writerow(YNAB_ROW_FIELDS)
        # write the data
        for ynab_row in ynab_data:
            csv_writer.writerow(ynab_row)

    return temp_file

def _open_ynab_for_import(file_path: str) -> None:
    pass

def main(input_filename: str, output_filename: str) -> None:
    """ Processes the input_file USAA csv file into a YNAB friendly file

    :param input_filename: The USAA formatted file to read in
    :param output_filename: The YNAB formatted file to write out
    """
    LOGGER.info(f"processing file: {input_filename}")
    usaa_data = _read_file(input_filename)
    ynab_data = _transform_usaa_to_ynab(usaa_data)
    output_filename = _write_ynab_file_out(ynab_data, file_path=output_filename)
    _open_ynab_for_import(output_filename)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.handlers.append(logging.StreamHandler())

    LOGGER.debug("running from __main__")
    main("./sample.csv", "./output.csv")