from pytorch_lightning.utilities import rank_zero_only
from pytorch_lightning.loggers import LightningLoggerBase
from pytorch_lightning.loggers.base import rank_zero_experiment
import json
from collections import defaultdict


class MyLogger(LightningLoggerBase):
    def __init__(self, exp_name):
        super().__init__()
        self.metrics = defaultdict(list)
        self.name = exp_name
        self.json_dict = {}
        self.json_dict["type"] = "Lightning"
        self.json_dict["exp_name"] = exp_name
        self.json_dict["Metrics"] = self.metrics

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    @rank_zero_experiment
    def experiment(self):
        # Return the experiment object associated with this logger.
        pass

    @property
    def version(self):
        # Return the experiment version, int or str.
        return "0.1"

    @rank_zero_only
    def log_hyperparams(self, params):
        # params is an argparse.Namespace
        # your code to record hyperparameters goes here
        pass

    @rank_zero_only
    def log_metrics(self, metrics, step):
        # metrics is a dictionary of metric names and values
        # your code to record metrics goes here
        for k, v in metrics.items():
            if k == "epoch":
                continue
            self.metrics[k].append([metrics[k], metrics["epoch"]])
            name = k
        pass

    @rank_zero_only
    def save(self):
        # Optional. Any code necessary to save logger data goes here
        # If you implement this, remember to call `super().save()`
        # at the start of the method (important for aggregation of metrics)
        super().save()
        with open("{}.json".format(self.name), "w") as fout:
            json.dump(self.json_dict, fout)

    @rank_zero_only
    def finalize(self, status):
        # Optional. Any code that needs to be run after training
        # finishes goes here
        pass
