class ScenarioSource:
    def get_scenarios(self):
        return [{"options": ""}] # Expects a list of dictionaries with command-line arguments.

class Analyzer:
    def analyze(self, out, err):
        if err:
            return {"output": out, "error": err} # Expects a dict.
        else:
            return {"output": out}

class Output:
    def output(self, keys, processed_code_results):
        print(keys)
        print(processed_code_results)

class DictListScenarioSource(ScenarioSource):
    def __init__(self, scenarios):
        self.scenarios = scenarios

    def get_scenarios(self):
        return self.scenarios

import re
class RegexAnalyzer(Analyzer):
    def __init__(self, regex, search_in_err=False):
        if isinstance(regex, re.Pattern):
            self.regex = regex
        else:
            self.regex = re.compile(regex)
        self.search_in_err = search_in_err

    def analyze(self, out, err):
        match = self.regex.match(err) if self.search_in_err else self.regex.match(out)
        if not match:
            return {}
        return match.groupdict()

import csv
from os import path

class CsvScenarioSource(ScenarioSource):
    def __init__(self, filepath, delimiter=",", quotechar="\""):
        assert path.exists(filepath)
        self.filepath = filepath
        self.delimiter = delimiter
        self.quotechar = quotechar

    def get_scenarios(self):
        keys = []
        scenarios = []
        with open(self.filepath, "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=self.delimiter, quotechar=self.quotechar)
            for i, row in enumerate(reader):
                if i == 0:
                    keys = row
                else:
                    scenarios += [dict(zip(keys, row))]
        return scenarios

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
