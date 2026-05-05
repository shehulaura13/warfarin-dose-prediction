
from sklearn.model_selection import GroupShuffleSplit
import pandas as pd

def split_data(df,group_col):

    rare_mask = df['cyp2c9'] == 0.0

    rare_df = df[rare_mask]
    rest_df = df[~rare_mask]


    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
   

# Split rare
    rare_idx = list(gss.split(rare_df, groups=rare_df[group_col]))[0]
    rare_train = rare_df.iloc[rare_idx[0]]
    rare_test = rare_df.iloc[rare_idx[1]]

# Split rest
    rest_idx = list(gss.split(rest_df, groups=rest_df[group_col]))[0]
    rest_train = rest_df.iloc[rest_idx[0]]
    rest_test = rest_df.iloc[rest_idx[1]]

    train_df = pd.concat([rare_train, rest_train])
    test_df = pd.concat([rare_test, rest_test])
    print("Total *3/*3:", (df['cyp2c9']==0.0).sum())
    print("Unique groups for *3/*3:", rare_df[group_col].nunique())
    print("*3/*3 in train:", (train_df['cyp2c9']==0.0).sum())
    print("*3/*3 in test:", (test_df['cyp2c9']==0.0).sum())

    return train_df,test_df

