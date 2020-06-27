from .building_blocks import Output

import csv

class CsvOutput(Output):
    def __init__(self, filepath, delimiter=",", quotechar="\""):
        self.filepath = filepath
        self.delimiter = delimiter
        self.quotechar = quotechar

    def output(self, keys, processed_code_results):
        with open(self.filepath, "w") as csvfile:
            writer = csv.writer(csvfile, delimiter=self.delimiter, quotechar=self.quotechar, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(keys)
            for result in processed_code_results:
                writer.writerow([result[key] if key in result else "" for key in keys])


