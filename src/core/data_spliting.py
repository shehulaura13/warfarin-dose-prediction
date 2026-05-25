from sklearn.model_selection import GroupShuffleSplit
import pandas as pd


def split_data(df, group_col):

   
    rare_mask = df["cyp2c9"] == 0.0  #*3/*3 genotype

    rare_df = df[rare_mask]
    rest_df = df[~rare_mask]

    # =====================================================
    # FIRST SPLIT:
    # temp_train (80%) vs test (20%)
    # =====================================================
    gss_test = GroupShuffleSplit(
        n_splits=1,
        test_size=0.2,
        random_state=42
    )

    # Rare split
    rare_idx = list(
        gss_test.split(
            rare_df,
            groups=rare_df[group_col]
        )
    )[0]

    rare_temp = rare_df.iloc[rare_idx[0]]
    rare_test = rare_df.iloc[rare_idx[1]]

    # Rest split
    rest_idx = list(
        gss_test.split(
            rest_df,
            groups=rest_df[group_col]
        )
    )[0]

    rest_temp = rest_df.iloc[rest_idx[0]]
    rest_test = rest_df.iloc[rest_idx[1]]

    
    temp_train_df = pd.concat([rare_temp, rest_temp])
    test_df = pd.concat([rare_test, rest_test])

    # =====================================================
    # SECOND SPLIT:
    # train (75% of temp) vs calibration (25% of temp)
    # =====================================================
    gss_cal = GroupShuffleSplit(
        n_splits=1,
        test_size=0.25,
        random_state=42
    )

    
    rare_temp_mask = temp_train_df["cyp2c9"] == 0.0
    rare_temp_df = temp_train_df[rare_temp_mask]
    rest_temp_df = temp_train_df[~rare_temp_mask]

    rare_idx2 = list(
        gss_cal.split(
            rare_temp_df,
            groups=rare_temp_df[group_col]
        )
    )[0]

    rare_train = rare_temp_df.iloc[rare_idx2[0]]
    rare_cal = rare_temp_df.iloc[rare_idx2[1]]

    # Rest split again
    rest_idx2 = list(
        gss_cal.split(
            rest_temp_df,
            groups=rest_temp_df[group_col]
        )
    )[0]

    rest_train = rest_temp_df.iloc[rest_idx2[0]]
    rest_cal = rest_temp_df.iloc[rest_idx2[1]]

    # Final datasets
    train_df = pd.concat([rare_train, rest_train])
    calibration_df = pd.concat([rare_cal, rest_cal])

    # =========================
    # Logging
    # =========================
    print("\n=== FINAL SPLITS ===")

    print("Train size:", len(train_df))
    print("Calibration size:", len(calibration_df))
    print("Test size:", len(test_df))

    print("\nRare CYP2C9 counts:")
    print("*3/*3 train:", (train_df["cyp2c9"] == 0.0).sum())
    print("*3/*3 calibration:", (calibration_df["cyp2c9"] == 0.0).sum())
    print("*3/*3 test:", (test_df["cyp2c9"] == 0.0).sum())

    return train_df, calibration_df, test_df

