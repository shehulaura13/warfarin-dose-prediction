import pandas as pd
import numpy as np
from src.utils.config import DATA_PROCESSED


def age_to_decade(age_str):
    if pd.isna(age_str):
        return np.nan
    try:
        age_str=str(age_str).strip()
        if "+" in age_str:
            lower= int(age_str.replace("+",""))
            return lower // 10

        if "-" in age_str:
            lower = int(age_str.split("-")[0])
            return lower // 10
        return int(age_str) // 10
    except :
        return np.nan
def basic_features(df):
    df = df.copy()
    if 'age' in df.columns:
        df["age_decade"] = df["age"].apply(age_to_decade)
        df = df.drop(columns=["age"], errors='ignore')
  
    if 'bmi' not in df.columns:
        df["bmi"] = df["weight_kg"]/(df["height_cm"]/100)**2

    return df

# -------------------------
# CYP2C9
# -------------------------
def clean_genotype(x):
    if pd.isna(x):
        return "UNKNOWN"
    return str(x).lower()

cyp2c9_map = {
    "*1/*1": 2.0,
    "*1/*2": 1.5,
    "*1/*3": 1.0,
    "*2/*2": 1.0,
    "*2/*3": 0.5,
    "*3/*3": 0.0
}
df_map = pd.DataFrame(
    list(cyp2c9_map.items()),
    columns=["genotype", "score"]
)
df_map.to_csv(DATA_PROCESSED/"cyp2c9_mapping.csv", index=False)



def cyp2c9_score(x):
   
    if '*1/*1' in x: return 2.0
    if '*1/*2' in x: return 1.5
    if '*1/*3' in x: return 1.0
    if '*2/*2' in x: return 1.0
    if '*2/*3' in x: return 0.5
    if '*3/*3' in x: return 0.0
    return 2.0


def genotype_cyp2c9(df):
    df['cyp2c9'] = df['cyp2c9_genotypes'].apply(clean_genotype).apply(cyp2c9_score)
   
    return df


# -------------------------
# VKORC1
# -------------------------
def normalize_vkorc1_1639(x):
    if pd.isna(x):
        return 'UNKNOWN'
    x = str(x).upper()

    if 'G/G' in x: return 'GG'
    if 'A/G' in x: return 'AG'
    if 'A/A' in x: return 'AA'
    return 'UNKNOWN'

def genotype_vkorc1_1639(df):
    col = 'vkorc1_1639'
    df['vkorc1'] = df[col].apply(normalize_vkorc1_1639)
    return df

# MEDICATIONS
# -------------------------
IMPORTANT_MEDS = ['amiodarone', 'aspirin', 'simvastatin', 'azole','fluconazole', 'metronidazole','ibuprofen','rifampin', 'carbamazepine', 'phenytoin']

def medication_features(df):
    med_list = []

    for row in df['medications']:
        features = {m: 0 for m in IMPORTANT_MEDS}

        if pd.notna(row):
            parts = str(row).lower().split(';')

            for p in parts:
                p = p.strip()

                for med in IMPORTANT_MEDS:
                    if med in p and not p.startswith('not'):
                        features[med] = 1

        med_list.append(features)

    med_df = pd.DataFrame(med_list)
    return pd.concat([df.reset_index(drop=True), med_df], axis=1)


# -------------------------
# COMORBIDITIES
# -------------------------
IMPORTANT_COMORB = ['hypertension', 'diabetes', 'heart_failure','heart_valve_replacement','liver_disease','renal_failure','cancer']


def comorbidity_features(df):
    com_list = []

    for row in df['comorbidities']:
        features = {c: 0 for c in IMPORTANT_COMORB}

        if pd.notna(row):
            parts = str(row).lower().split(';')

            for p in parts:
                for c in IMPORTANT_COMORB:
                    if c in p:
                        features[c] = 1

        com_list.append(features)

    com_df = pd.DataFrame(com_list)
    return pd.concat([df.reset_index(drop=True), com_df], axis=1)

def merge_binary_cols(df, cols):
    return df[cols].fillna(0).max(axis=1)



# -------------------------
# FINAL PIPE
def create_features(df):
    df = basic_features(df)
    df = genotype_cyp2c9(df)
    df = genotype_vkorc1_1639(df)
    df = medication_features(df)
    df = comorbidity_features(df)
    df["amiodarone"] = merge_binary_cols(df,["amiodarone", "amiodarone_cordarone"])
    df["simvastatin"] = merge_binary_cols(df,["simvastatin", "simvastatin_zocor"])
    df["carbamazepine"] = merge_binary_cols(df, ["carbamazepine", "carbamazepine_tegretol"])
    df["rifampin"] = merge_binary_cols(df,["rifampin_or_rifampicin", "rifampin"])
    df["phenytoin"] = merge_binary_cols(df, ["phenytoin", "phenytoin_dilantin"])
    df.drop(columns=[
    "amiodarone_cordarone",
    "simvastatin_zocor",
    "carbamazepine_tegretol",
    "phenytoin_dilantin",
    "rifampin_or_rifampicin"
    ], inplace=True, errors="ignore")
    


    raw_genotype_cols = ['vkorc1_1639','cyp2c9_genotypes']

    raw_text_cols = [
    'medications',
    'comorbidities'
   ]

    cols_to_drop = raw_text_cols + raw_genotype_cols

    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])


    df=df.loc[:, ~df.columns.duplicated()]
    return df




    

   


