from .building_blocks import ScenarioSource

import itertools

class CombineScenarios(ScenarioSource):
    ZIP = 0
    PRODUCT = 1
    
    def __init__(self, *args, **kwargs):
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
        scenario_lists = map(lambda s: s.get_scenarios(), self.scenario_sources)
        if self.mode == self.ZIP:
            return list(map(self.__combine_tuple, zip(*scenario_lists)))
        elif self.mode == self.PRODUCT:
            return list(map(self.__combine_tuple, itertools.product(*scenario_lists)))
        else:
            return []


class DictListScenarioSource(ScenarioSource):
    def __init__(self, scenarios):
        self.scenarios = scenarios

    def get_scenarios(self):
        return self.scenarios

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

