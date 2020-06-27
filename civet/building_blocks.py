class ScenarioSource:
    """The superclass for anything that provides scenarios to a Civet instance."""

    def get_scenarios(self):
        """Returns a list of dicts, each dict representing a scenario.  In this implementation, returns ["options": ""}]."""
        return [{"options": ""}]


class Analyzer:
    """The superclass for anything that analyzes the results from a Civet scenario.  These classes should be as minimal as possible, each doing a very narrow and well-defined job.  If you want to gather six data points with no real relation to each other, write six analyzers and chain them together in your Civet instance."""

    def analyze(self, out, err):
        """Takes in text from a completed scenario and performs some kind of processing on it.
        Args:
            out: A string representing the text that the scenario produced on STDOUT.
            err: A string representing the text that the scenario produced on STDERR.

        Returns:
            A dict of key-value pairs representing the data derived from the raw STDOUT and STDERR text.  In this implementation, returns {"output": out, "error": err} with no further processing, or simply {"output": out} if there is no error text.
        """
        if err:
            return {"output": out, "error": err}
        else:
            return {"output": out}


class Output:
    """The superclass for anything that prints out processed results from a completed set of Civet scenarios."""

    def output(self, keys, processed_code_results):
        """"Formats and outputs data to some endpoint.  In this implementation, prints to STDOUT.

        Args:
            keys: A list of all the keys that appear in the key-value pairs in processed_code_results.  **Not all keys will appear in all result dicts, in general.**  The exceptions are the first two elements, "id" and "command", which represent an ID number for each scenario and the command to reproduce said scenario.
            processed_code_results: A list of dicts, each representing the amalgamated results from running one scenario.
        """
        print(keys)
        print(processed_code_results)
