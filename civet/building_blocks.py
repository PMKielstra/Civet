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
