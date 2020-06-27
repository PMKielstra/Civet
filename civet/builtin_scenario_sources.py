from .building_blocks import ScenarioSource

import itertools

class CombineScenarios(ScenarioSource):
    """Combines several scenario sources, each contributing different elements, into one.  For instance, if scenario source A contributes [{"a": 1}] and source B contributes [{"b": 2}], then CombineScenarios(A, B).get_scenarios() would return [{"a": 1, "b": 2}].

    Attributes:
        *args: A list of ScenarioSource instances.
        mode: A keyword argument with two possible values, CombineScenarios.ZIP (in which scenario lists are zipped together, combining A[1] with B[1], A[2] with B[2], and so on), and CombineScenarios.PRODUCT (in which scenario lists are combined with a Cartesian product, combining A[1] with B[1], A[1] with B[2], A[2] with B[1], A[2] with B[2], and so on).
    """
    ZIP = 0
    PRODUCT = 1
    
    def __init__(self, *args, **kwargs):
        """Initializes CombineScenarios and checks that all members of *args are in fact ScenarioSource instances."""
        assert len(args) > 0
        for a in args:
            assert isinstance(a, ScenarioSource)
        
        self.mode = kwargs.pop("mode", self.ZIP)
        assert self.mode in [self.ZIP, self.PRODUCT]
        
        self.scenario_sources = list(args)

    def __combine_tuple(self, to_be_combined):
        result = {}
        for t in to_be_combined:
            result.update(t)
        return result

    def get_scenarios(self):
        """Queries each scenario source for its list of scenarios and combines the results."""
        scenario_lists = map(lambda s: s.get_scenarios(), self.scenario_sources)
        if self.mode == self.ZIP:
            return list(map(self.__combine_tuple, zip(*scenario_lists)))
        elif self.mode == self.PRODUCT:
            return list(map(self.__combine_tuple, itertools.product(*scenario_lists)))
        else:
            return []


class DictListScenarioSource(ScenarioSource):
    """Returns a hardcoded list of scenarios."""
    def __init__(self, scenarios):
        self.scenarios = scenarios

    def get_scenarios(self):
        return self.scenarios

import csv
from os import path

class CsvScenarioSource(ScenarioSource):
    """Pulls scenarios from a CSV.  The first row is assumed to contain headers, giving the names of each column.  These determine the elements of the Civet command into which each member of any given row below the first is interpolated.

    Attributes:
        filepath: The path to the CSV file.  Can be relative.
        delimiter: The CSV delimiter.  By default, it's a comma.
        quotechar: The CSV quote character.  By default, it's a double-quote.
    """
    def __init__(self, filepath, delimiter=",", quotechar="\""):
        """Initializes a CSVScenarioSource.  Does not check if the CSV file exists."""
        self.filepath = filepath
        self.delimiter = delimiter
        self.quotechar = quotechar

    def get_scenarios(self):
        """Checks if the CSV file exists, and, if it does, reads a list of scenarios from it.

        Raises:
            AssertionError: If the CSV file from the constructor doesn't exist.
        """
        assert path.exists(filepath)
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

