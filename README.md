# Prophetest

**This repo is for artifact evaluation of submission #678.**

We upload the constructed Markov Chains and Ground Truth  classified by tool and app category.



We also open source our code in `Code/`.

`GetHash.py` contains the state and widget abstraction algorithms we used in our paper.

`BatchBuildGraph1.py` and `BatchBuildGraph2.py` refer to the algorithms constructing Markov Chains of Monkey and WCTester from the raw UI trasition traces, respectively.

`CountMonkey.py` gets the ground-truth of Monkey and WCTester's test runs.

`calculate.py, evaluation.py, experiment.py, metrics.py, predict.py` are used for calculating stable distributions, stopping times, communication bottlenecks from the constructed Markov Chains.

`saturation_point.py, tool_selection.py theory_accuracy.py` represent the code to get the experimental results for three RQs, respectively.

`data4paper.zip` contains all experimental results appearing in the paper.



In addition, we upload all raw traces clloected using Toller tool at https://github.com/anonymousForICSEReview/traces/releases/tag/icse22

