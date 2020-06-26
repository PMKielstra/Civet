import subprocess
import shlex

class Civet:
    __default_options = { "serial": False, "stdout_stderr_encoding": "utf-8"  }
    
    def __init__(self, options = {}, command="", scenario_sources=[], analyzers=[], outputs=[]):
        self.options = self.__default_options
        self.options.update(options)
        self.command = command
        self.scenario_sources = scenario_sources
        self.analyzers = analyzers
        self.outputs = outputs

    def use_command(self, command):
        return Civet(self.options, command, self.scenario_sources, self.analyzers, self.outputs)

    def get_scenarios_from(self, source):
        return Civet(self.options, self.command, self.scenario_sources + [source], self.analyzers, self.outputs)

    def analyze_with(self, analyzer):
        return Civet(self.options, self.command, self.scenario_sources, self.analyzers + [analyzer], self.outputs)

    def output_to(self, output):
        return Civet(self.options, self.command, self.scenario_sources, self.analyzers, self.outputs + [output])

    def run(self):
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
            formatted_command = shlex.split(self.command.format(**scenario)) # Scenario is a dict, so we ** to apply it.
            proc = subprocess.Popen(formatted_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            running_processes += [(formatted_command, proc)]
            if self.options["serial"]: # Wait for each process to finish before setting up the next one.
                proc.wait()

        #Process raw outputs
        processed_code_results = []
        keys = set()
        for i, (formatted_command, proc) in enumerate(running_processes):
            processed = {"id": i, "command": " ".join(formatted_command)}
            out, err = map(lambda s: s.decode(self.options["stdout_stderr_encoding"]), proc.communicate())
            for analyzer in self.analyzers:
                processed.update(analyzer.analyze(out, err))
            processed_code_results += [processed]
            keys = keys.union(set(processed.keys())) # Keep track of all keys returned from all processed output.

        keys = list(keys)
        keys.sort(key=lambda x: 1 if x == "id" or x == "command" else 2)

        for output in self.outputs:
            output.output(keys, processed_code_results)
