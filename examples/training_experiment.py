try:
    from sklearn.datasets import load_digits, load_iris
except ImportError:
    print("Please install scikit-learn to run this example")
    raise
import hydra 
import pandas as pd
from experiment_tracker import hydra_utils

@hydra.main(config_path=".", config_name="config")
def main(cfg):

    hydra_utils.save_hash(cfg)
    print("Dataset:", cfg.dataset)
    if cfg.dataset == "digits":
        digits = load_digits()
        X = digits.data
        y = digits.target

        X_train = X[:1000]
        y_train = y[:1000]
        X_test = X[1000:]
        y_test = y[1000:]

    elif cfg.dataset == "iris":
        iris = load_iris()
        X = iris.data
        y = iris.target

        X_train = X[:100]
        y_train = y[:100]
        X_test = X[100:]
        y_test = y[100:]
    else:
        raise ValueError("Dataset not supported")
    
    print("X shape:", X.shape)
    print("y shape:", y.shape)
    
    
    if cfg.estimator == "random_forest":
        from sklearn.ensemble import RandomForestClassifier
        clf = RandomForestClassifier(n_estimators=50, n_jobs=-1, random_state=cfg.seed)
    elif cfg.estimator == "svm":    
        from sklearn.svm import SVC
        clf = SVC()
    elif cfg.estimator == "knn":
        from sklearn.neighbors import KNeighborsClassifier
        clf = KNeighborsClassifier(n_neighbors=5, n_jobs=-1)

    clf.fit(X_train, y_train)

    res_train = clf.predict(X_train)
    res_test = clf.predict(X_test)

    # Save a dictionary with the results
    df_train = pd.DataFrame({"y_true": y_train, "y_pred": res_train})
    df_test = pd.DataFrame({"y_true": y_test, "y_pred": res_test})
    df_train.to_csv("train.pkl")
    df_test.to_csv("test.pkl")



if __name__ == "__main__":
    main()