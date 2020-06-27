from civet import *

Civet().use_command("ls {args}") \
                        .get_scenarios_from(CsvScenarioSource("argslist.csv")) \
                        .analyze_with(RegexAnalyzer("(?P<firstbit>(.|\n)*argslist)")) \
                        .analyze_with(RegexAnalyzer("argslist(?P<lastbit>(.|\n)*)")) \
                        .output_to(CsvOutput("output.csv")) \
                        .output_to(Output()) \
                        .run()
