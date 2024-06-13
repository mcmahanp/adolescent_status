This is replication code for _Status Ambiguity and Horizontality Among Adolescents_.

Due to the sensitive nature of the the data, this is not a complete pipeline from Add Health wave 1 to the final output. The most important parts of the analytical pipeline are present, however:

1. `OrderEstimator` is included as a submodule from <https://github.com/mcmahanp/OrderEstimator>. This is the general-purpose code to estimate status relations from an asymmetric adjacency matrix.
2. `create_anon_graphs.py` creates anonymized GraphML files from Add health friendship nomination data.
3. `ranking_order_parallel.py` uses `OrderEstimator` to estimate status relations on each of the anonymized networks.
4. `analyze_traces.py` creates status-relation DAGs from the output traces in the previous step.
5. `merge_node_data.R` merges data from raw Add Health files and calculates relevant variables.
6. `regressions.R` performs the regressions and saves the results to disk.


 <p xmlns:cc="http://creativecommons.org/ns#" >This work is licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC BY-NC-SA 4.0<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/nc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/sa.svg?ref=chooser-v1" alt=""></a></p> 