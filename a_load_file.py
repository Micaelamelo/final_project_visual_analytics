from pathlib import Path
import pandas as pd


##############################################
# Implement the below method
# The method should be dataset-independent
##############################################
def read_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=",")
    pass


if __name__ == "__main__":
    dataset = read_dataset(Path('..', '..', 'iris.csv'))
    assert type(dataset) == pd.DataFrame
    print("ok")
