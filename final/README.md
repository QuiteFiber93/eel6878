This are four main components to these files: the report, the code, the data, and the plots.

The report is a pdf file named "EEL_6878_Final_Project.pdf".

There are four code files.
    - plot_network.py generates an image of the network graph used in the project.
    - network_analysis.py generates the ground truth answers used in evaluating LLM performance.
    - run_batch.py generates and submits queries to Claude Sonnet 4.5 in batch, then records the responses.
    - analysis.py uses the results from network_analysis and run_batch to generate the plots used in the report.

There are four data files.
    - network_graph.edgelist was used to generate the graph for the report.
    - ground_truth.json contains the results from network_analysis.py.
    - llm_responses.json contains the responses from the LLM queries.
    - llm_prompt.txt contains the template used to generate queries for the LLM.

The plots folder contains all of the plots used in the report.