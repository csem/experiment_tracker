python3 -m pdb  examples/training_experiment.py -m seed=1,2,3,43 dataset=digits,iris normalise=True,False
python3 -m pdb examples/training_experiment.py -m estimator=svm,knn dataset=digits,iris normalise=True,False
python3 -m pdb examples/training_experiment.py -m trigger_error=True dataset=digits