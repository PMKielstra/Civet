import subprocess
import shlex

from .building_blocks import ScenarioSource, Analyzer, Output


class Civet:
    """The main Civet class.  Implements a builder pattern to create and run Civet instances.

    Currently supports the following options:
     - serial: If this is True, scenarios will be run one after the other instead of in some form of parallel.  (Default: False.)
     - stdout_stderr_encoding: The encoding to use when decoding bytes from completed scenarios' stdout and stderr into strings.  (Default: "utf-8".)

    Attributes:
        options: A dict containing all options set by the user.  Optional.  Leaving out a key is treated as giving it the default value.
        command, scenario_sources, analyzers, otuputs: Handled by the builder logic.

    """

    __default_options = {"serial": False, "stdout_stderr_encoding": "utf-8"}

    def __init__(self, options={}, command="", scenario_sources=[], analyzers=[], outputs=[]):
        """Initializes Civet and apply default values to any options that have not been passed in."""
        self.options = self.__default_options
        self.options.update(options)
        self.command = command
        self.scenario_sources = scenario_sources
        self.analyzers = analyzers
        self.outputs = outputs

    def use_command(self, command):
        """Creates a Civet instance identical to this one but using the passed-in command."""
        assert isinstance(command, str)
        return Civet(self.options, command, self.scenario_sources, self.analyzers, self.outputs)

    def get_scenarios_from(self, source):
        """Creates a Civet instance identical to this one but adding the passed-in scenario source to the list of scenario sources to use."""
        assert isinstance(source, ScenarioSource)
        return Civet(self.options, self.command, self.scenario_sources + [source], self.analyzers, self.outputs)

    def analyze_with(self, analyzer):
        """Creates a Civet instance identical to this one but adding the passed-in analyzer to the list of analyzers to use."""
        assert isinstance(analyzer, Analyzer)
        return Civet(self.options, self.command, self.scenario_sources, self.analyzers + [analyzer], self.outputs)

    def output_to(self, output):
        """Creates a Civet instance identical to this one but adding the passed-in output to the list of outputs to use."""
        assert isinstance(output, Output)
        return Civet(self.options, self.command, self.scenario_sources, self.analyzers, self.outputs + [output])

    def __sort_id_command_else(self, s):
        if s == "id":
            return 1
        elif s == "command":
            return 2
        else:
            return 3

    def run(self):
        """Gathers all scenarios (calling get_scenarios on all scenario sources), runs all processes, and analyzes and outputs results."""
        # Sanity checking
        assert len(self.command) > 0
        assert len(self.scenario_sources) > 0
        assert len(self.analyzers) > 0
        assert len(self.outputs) > 0

        # Build scenario list
        scenarios = []
        for source in self.scenario_sources:
            scenarios += source.get_scenarios()
        assert len(scenarios) > 0

        # Spin up all processes at once, for parallelism
        running_processes = []
        for scenario in scenarios:
            # Scenario is a dict, so we ** to apply it.
            formatted_command = shlex.split(self.command.format(**scenario))
            proc = subprocess.Popen(
                formatted_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            running_processes += [(formatted_command, proc)]
            # Wait for each process to finish before setting up the next one.
            if self.options["serial"]:
                proc.wait()

        # Process raw results
        processed_code_results = []
        keys = set()
        for i, (formatted_command, proc) in enumerate(running_processes):
            processed = {"id": i, "command": " ".join(formatted_command)}
            out, err = map(lambda s: s.decode(
                self.options["stdout_stderr_encoding"]), proc.communicate())
            for analyzer in self.analyzers:
                processed.update(analyzer.analyze(out, err))
            processed_code_results += [processed]
            # Keep track of all keys returned from all processed output.
            keys = keys.union(set(processed.keys()))

        # Output processed results
        keys = list(keys)
        keys.sort(key=self.__sort_id_command_else)

        for output in self.outputs:
            output.output(keys, processed_code_results)
