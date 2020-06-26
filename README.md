# Civet
Civet runs many instances of a particular program at once.

## Using Civet

```
options = {}
Civet(options).use_command("ls {args}") \
	.get_scenarios_from(ScenarioSource()) \
	.analyze_with(Analyzer()) \
	.output_to(Output()) \
	.run()
```

Civet has the following core way of doing things:

1. Set a command, complete with named points for interpolating arguments that differ between scenarios.
2. Collect scenarios from a variety of sources.
3. Run the scenarios, in serial or parallel.
4. Analyze the output from each scenario, getting a list of key-value pairs of data.
5. Write out these key-value pairs in some way.


