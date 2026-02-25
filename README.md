# Master Thesis Project
This repository contains all the code used for the master thesis project.


## Data Analysis

The folder `data_analysis` contains all notebooks and code used to analyse the expert data



## Data Augmentation

The folder `data_augmentation` contains all notebooks and code used to analyse the clean and enhance the expert data


## Evaluation

The folder `evaluation` contains all notebooks and code used to evaluate the search results created by the experimental runs


## Experimental runs

The folder `experimental_runs` contains alls the notebooks used to run the experiments. This includes the setup and implementation of the search methods


## Test Collections

The folder `test_collection` contains all the code and notebooks to create the test collection which is for experiments and evaluation.
This contains the creation of search queries, document pooling and relevance assessment.
For the code for the relevance assessment is in folder `test_collection/relevance_judgements/umbrela`, which is an adaption of https://github.com/castorini/umbrela/tree/main!

All the datasets used in the notebooks and code are accessible here:

| Datensatz | Zenodo (DOI) |
|---|---|
| Expertenprofile und Suchlogs (Rohdaten) | https://doi.org/10.5281/zenodo.18762496 |
| Erweiterte Expertenprofile | https://doi.org/10.5281/zenodo.18762697 |
| Testkollektion (Qrels, Pool, Suchanfragen) | https://doi.org/10.5281/zenodo.18762321 |
| Relevanzbewertungen von GPT und Mensch | https://doi.org/10.5281/zenodo.18760712 |
| Suchergebnisse der Suchmethoden | https://doi.org/10.5281/zenodo.18760569 |
| Evaluationsergebnisse der Suchmethoden | https://doi.org/10.5281/zenodo.18771958 |