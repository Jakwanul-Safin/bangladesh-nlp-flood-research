from typing import Optional
import os
import pandas as pd

def load_dataset(index: Optional[int] = None, 
                name: Optional[str] = None, 
                _id: Optional[str] = None, 
                filepath: Optional[str] = None, 
                ROOT:str=''
            ):
    datasets = pd.read_csv(os.path.join(ROOT, "classification_datasets.csv"), index_col="index")
    if index is not None:
        row = datasets.iloc[index]
    elif name is not None:
        try:
            row = next(entry for i, entry in datasets.iterrows() if entry.dataset_name == name)
        except StopIteration:
            raise KeyError(f"Could not find dataset for name: {name}")
    elif _id is not None:
        try:
            row = next(entry for i, entry in datasets.iterrows() if entry.identifier == _id)
        except StopIteration:
            raise KeyError(f"Could not find dataset for id: {_id}")
    elif filepath is not None:
        path = filepath
        identifier = None
        return pd.read_csv(os.path.join(ROOT, path)), identifier
    else:
        raise ValueError("Did not specify dataset to load")

    name, path, identifier, desc = row
    print(f"Loaded {name} dataset")
    return pd.read_csv(os.path.join(ROOT, path), index_col=0), identifier

def getFivefoldStandard(ROOT = "", USE_TRANSLATED = False):
    df, identifier = load_dataset(_id = "rfft", ROOT = ROOT)
    X_trains, X_tests, y_trains, y_tests = [[df[col][df[f"split_{i}"] == cat] for i in range(5)]
            for col in ('content' if not USE_TRANSLATED else 'translated', 'is_flood') 
            for cat in ('test', 'train')
           ]
    print(f"{len(y_trains)} folds\n{len(y_trains[0])} training examples\n{len(y_tests[0])} test examples")
    return df, identifier, X_trains, X_tests, y_trains, y_tests

def getFivefoldWithUnlabelled(ROOT = ""):
    df, identifier = load_dataset(_id = "sffu", ROOT = ROOT)
    df_u = df[df['label']==-1]
    df_l = df[df['label']!=-1]
    X_u = df_u
    X_tests, X_trains, y_tests, y_trains = [[df_l[col][df_l[f"split_{i}"] == cat] for i in range(5)]
            for col in ('text', 'label') 
            for cat in ('test', 'train')
           ]
    print(f"{len(y_trains)} folds\n{len(X_u)} unlabelled examples\n{len(y_trains[0])} labelled training examples\n{len(y_tests[0])} labelled test examples")
    return df, identifier, X_trains, X_tests, y_trains, y_tests, X_u

def getEnglishDataset(ROOT = ""):
    eng_df, identifier = load_dataset(_id = "rtte", ROOT = ROOT)
    eng_train_dt = eng_df[eng_df['type'] == 'train']
    eng_test_dt = eng_df[eng_df['type'] == 'test']
    eng_X_train, eng_y_train = eng_train_dt['text'], eng_train_dt['is_flood']
    eng_X_test, eng_y_test = eng_test_dt['text'], eng_test_dt['is_flood']
    print(f"English Examples\n{len(eng_X_train)} training examples\n{len(eng_X_test)} test examples")
    return eng_df, identifier, eng_X_train, eng_X_test, eng_y_train, eng_y_test
