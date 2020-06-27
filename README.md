# Civet
Civet runs many instances of a particular program at once.

## Installing

```
git clone https://github.com/PMKielstra/Civet
cd Civet
pip install -e .
```


## Using Civet

```
options = {}
Civet(options).use_command("command") \
	.get_scenarios_from(ScenarioSource()) \
	.analyze_with(Analyzer()) \
	.output_to(Output()) \
	.run()
```

To run a Civet instance, you need four things: a command, a scenario source, an analyzer, and an output.  You can have more than one of all these things except the command.

### Commands
Civet is designed to run basically the same command over and over, with changes to the arguments.  This is done with Python string interpolation: everything you want to change is replaced with a name inside curly brackets.  To test a differential-equation solver, for instance, we might use `"./solvediffeq --equation {equation} --max-iterations {maxiter}"`.  Civet will then expect its scenarios to provide values for `equation` and `maxiter`.

### Scenarios
Scenarios are simply lists of values for the variables within a given command string.  They take the form of dicts, so a valid scenario for our differential-equation solver might be `{"equation": "du/dx=5u", "maxiter": "50"}`.  Civet pulls scenarios from scenario sources, which extend the `ScenarioSource` class and are simple to customize.  It does, however, come with a few built-in options.

`DictListScenarioSource` takes a hardcoded list of scenarios in the constructor and passes that on to Civet.  If we wanted to test only that equation, but with two `maxiter` values, we might use `Civet().get_scenarios_from(DictListScenarioSource([{"equation": "du/dx=5u", "maxiter": "50"}, {"equation": "du/dx=5u", "maxiter": "100" ]))`.

`CsvScenarioSource`, on the other hand, pulls data from a CSV, formatted with a header row.  If we put
```
equation,maxiter
du/dx=5u,50
du/dx=5u,100
```
into `scenarios.csv` and ran `Civet().get_scenarios_from(CsvScenarioSource("scenarios.csv"))`, we would have the same result as in the `DictListScenarioSource` example.

Using multiple scenario sources is not only allowed but encouraged.  `Civet().get_scenarios_from(A).get_scenarios_from(B)` will run all scenarios from `A` and all scenarios from `B`.  It will even run them in that order, if you run in serial.

#### Combining Scenarios
Civet automatically combines results from different scenario sources into one overarching list of scenarios.  However, sometimes you want to combine information from multiple scenario sources to form one scenario.  For example, you might have a CSV listing differential equations, and know that you want to run each of them with `maxiter 50` and `maxiter 100`.  For this, Civet has the `CombineScenarios` scenario source.

Say we have a file, `diffeqlist.csv`, which looks like
```
equation
du/dx=5u
du/dx=5u+1
du/dx=u^2
...
```

Then `CombineScenarios(DictListScenarioSource([{"maxiter":"50"}, {"maxiter":"100"}]), CsvScenarioSource("diffeqlist.csv"))` will take the Cartesian product of the scenarios coming from both lists to get an eventual list of scenarios that looks like `{"equation": "du/dx=5u", "maxiter":"50"}, {"equation": "du/dx=5u", "maxiter":"100"}, {"equation": "du/dx=5u+1", "maxiter":"50"}...`.

`CombineScenarios` can take any number of scenario sources.  It is itself a scenario source, so all you have to do is pass it to `get_scenarios_from` like any other scenario source.

### Analyzers
Once you produce a command and a set of scenarios, Civet has everything it needs to run your code.  However, the result would be a lot of text, and that's not helpful.  For this reason, output in Civet is mediated through Analyzers.  These take in the STDOUT and STDERR from running any given scenario, perform some kind of analysis on it, and spit out the results.  They are subclasses of the `Analyzer` class, and, as with scenario sources, you are encouraged to write your own.

Analyzers contain a single function: `analyze(self, out, err)`.  This returns a dict containing derived information.  For example, we might notice that our differential-equation solver always finishes its output with `Total time: 12s` or something of the sort, and write a `DiffEqTimeAnalyzer` which, when given a string that ends with that, would return `{"totaltime":"12"}`.

When you call `analyze_with` multiple times to use multiple analyzers, each one gets to analyze each scenario in isolation and then the results are combined to give a full analysis.  If we had another analyzer, `OneHalfTimeAnalyzer`, which would find one half of the total time, and ran `Civet()...analyze_with(DiffEqTimeAnalyzer()).analyze_with(OneHalfTimeAnalyzer))`, we would eventually get analysis results that looked something like `{"totaltime":"12", "halftime":"6"}`.  The total time was contributed by the former analyzer and the half time by the latter.  Individual analyzers can of course return dicts with more than one element, as well.

Civet comes with two useful analyzers.  The first, the base `Analyzer()`, simply returns the entire STDOUT and, if there is any, the entire STDERR.  The second, `RegexAnalyzer()`, searches in either STDOUT or STDERR for a regular-expression match.  The regex should contain some number of [named capturing groups](https://docs.python.org/3/howto/regex.html#non-capturing-and-named-groups).  The names of the groups will be the keys in the dict returned, and the captured strings will be the values.

### Outputs
Having analyzed the result from each of our scenarios, Civet needs somewhere to send it.  It could print it to a terminal, write to a file, or do something more exotic.  This is all handled with outputs, subclasses of `Output`.

Outputs receive a list of keys, containing every key that an Analyzer has produced from at least one scenario, and a list of dicts, each representing a scenario.  Civet adds two more fields to each scenario, beyond what the Analyzers produce: `"id"`, a unique ID, and `"command"`, the actual command that Civet ran, verbatim, in that scenario.  These are included in the list of keys.

The base `Output()` writes first the list of keys and the results to the terminal.  `CsvOutput()` writes them to a CSV file instead.

Using multiple outputs will output the same data in different places.

### Options
Civet currently supports two options:

```
options = {
"serial": False # Run scenarios one after the other instead of in parallel
"stdout_stderr_encoding": "utf-8" # The text encoding used on STDOUT and STDERR by whatever program you will invoke
}
```

### Putting it all together

Let's go through our differential equation example from the top.  We want to run Civet in parallel, and UTF-8 is a perfectly OK encoding to use, so we don't need to pass in any options, and we can get started with a trivial constructor:

```
Civet()
```

There are two things we want to interpolate into our command, the equation and the maximum number of iterations to use, so we wrap those things in curly brackets to get

```
Civet().use_command("./solvediffeq --equation {equation} --max-iterations {maxiter}")
```

For simplicity, we'll say we have a CSV file with all our scenarios in it, giving

```
Civet().use_command("./solvediffeq --equation {equation} --max-iterations {maxiter}") \
	.get_scenarios_from(CsvScenarioSource("scenarios.csv"))
```
We'll analyze it with a couple of regex analyzers, to get the total time and the number of iterations:

```
Civet().use_command("./solvediffeq --equation {equation} --max-iterations {maxiter}") \
	.get_scenarios_from(CsvScenarioSource("scenarios.csv")) \
	.analyze_with(RegexAnalyzer("(.|\n)*Total time: (?P<time>[0-9]+)")) \
	.analyze_with(RegexAnalyzer("(.|\n)*(?P<iters>[0-9]+) iterations used"))
```
Finally, we'll output our results to the terminal and to a CSV file, and run the program:

```
Civet().use_command("./solvediffeq --equation {equation} --max-iterations {maxiter}") \
	.get_scenarios_from(CsvScenarioSource("scenarios.csv")) \
	.analyze_with(RegexAnalyzer("(.|\n)*Total time: (?P<time>[0-9]+)")) \
	.analyze_with(RegexAnalyzer("(.|\n)*(?P<iters>[0-9]+) iterations used")) \
	.output_to(CsvOutput("output.csv")).output_to(Output()) \
	.run()
```

This will create a CSV file that looks something like

```
id,command,time,iters
0,"./solvediffeq --equation du/dx=5u --max-iterations 50",2,44
1,"./solvediffeq --equation du/dx=4u^2 --max-iterations 95",6,87
...
```
and print the same output, although in a different format, to the terminal.
