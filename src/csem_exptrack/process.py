import numpy as np

def normalize_confusion_matrix(cm, mode="recall"):
    if mode == "recall":
        cm = np.round(cm.astype("float") / cm.sum(axis=1)[:, np.newaxis], 2)
    else:
        cm = np.round(cm.astype("float") / cm.sum(axis=0)[np.newaxis, :], 2)
    return cm