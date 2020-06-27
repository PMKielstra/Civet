from .building_blocks import Analyzer

import re

class RegexAnalyzer(Analyzer):
    """Matches a regular expression to either the STDOUT or the STDERR and returns the key-value pairs from named capturing groups.  For example, using the regex "colou?r" would return nothing, because it has no named capturing groups, but using the regex "col(?P<ou_or_o>ou?)r" would return either "o" or "ou" for the first instance of either color or colour.

    Attributes:
        regex: The regex (Python flavour, obviously) to search for.  Can be either a re.Pattern or a string.
        search_in_err: Search in STDERR result instead of STDOUT.  False by default.
    """
    def __init__(self, regex, search_in_err=False):
        """Initializes the RegexAnalyzer and compiles the passed-in regex if it hasn't been compiled already."""
        if isinstance(regex, re.Pattern):
            self.regex = regex
        else:
            self.regex = re.compile(regex)
        self.search_in_err = search_in_err

    def analyze(self, out, err):
        """Calls regex.match on STDOUT or STDERR, depending on configuration.

        Returns:
            The groupdict that results from the match, or {} if no match was found.
        """
        match = self.regex.match(err) if self.search_in_err else self.regex.match(out)
        if not match:
            return {}
        return match.groupdict()
