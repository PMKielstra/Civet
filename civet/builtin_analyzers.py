from .building_blocks import Analyzer

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
