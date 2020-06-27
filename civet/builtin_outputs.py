from .building_blocks import Output

import csv

class CsvOutput(Output):
    """Outputs to a CSV, producing a file with a header row and then one row for each scenario.

    Attributes:
        filepath: The path to the CSV.  Can be relative.  Will overwrite existing files.
        delimiter: The delimiter to use.  By default, it's a comma.
        quotechar: The quote character to use.  By default, it's a double quote."""
    def __init__(self, filepath, delimiter=",", quotechar="\""):
        """Initialize CsvOutput."""
        self.filepath = filepath
        self.delimiter = delimiter
        self.quotechar = quotechar

    def output(self, keys, processed_code_results):
        """Write out first the keys (the header row) and then the processed results to the CSV file."""
        with open(self.filepath, "w") as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter, quotechar=self.quotechar, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(keys)
            for result in processed_code_results:
                writer.writerow([result[key] if key in result else "" for key in keys])


