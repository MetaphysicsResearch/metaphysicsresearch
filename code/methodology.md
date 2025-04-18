https://artificialanalysis.ai/methodology/intelligence-benchmarking

General Testing Parameters
We test all evals with the following settings:

Temperature: 0
Maximum output tokens:
Non-reasoning models: 4,096 tokens (adjusted downward where models have a smaller context window, or lower maximum output tokens cap)
Reasoning models: Maximum output tokens allowed, as disclosed by model creators (custom setting for each reasoning model)
Code evaluation environment:
Ubuntu 22.04 LTS
Python 3.12
Error handling:
Automatic retry on API failures (up to 30 attempts)
All questions that failed all 30 retries are manually reviewed. Results where persistent API failures have caused issues are not published. Errors where all available APIs for proprietary models block a certain question may lower scores (this effect is not material)
We maintain internal copies of all evaluation datasets. The sources of our selected datasets are listed below.