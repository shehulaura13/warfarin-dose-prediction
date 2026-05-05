


def clean_data(df):
    df = df.copy()
    df = df.dropna(subset=['Therapeutic Dose of Warfarin'])
    df['target'] = df['Therapeutic Dose of Warfarin']
    df = df.drop(columns=['Unnamed: 63', 'Unnamed: 64', 'Unnamed: 65','Therapeutic Dose of Warfarin',
                          'Target INR', 
                          'Indication for Warfarin Treatment',
                          'Estimated Target INR Range Based on Indication',
                          'Subject Reached Stable Dose of Warfarin','INR on Reported Therapeutic Dose of Warfarin',
                          'Atorvastatin (Lipitor)', 'Fluvastatin (Lescol)',
                          'Lovastatin (Mevacor)', 'Pravastatin (Pravachol)',
                          'Rosuvastatin (Crestor)', 'Cerivastatin (Baycol)',
                          'Genotyped QC Cyp2C9*2', 'Genotyped QC Cyp2C9*3',
                          'Combined QC CYP2C9', 'VKORC1 QC genotype: -1639 G>A (3673); chr16:31015190; rs9923231; C/T',
                          'VKORC1 genotype: 497T>G (5808); chr16:31013055; rs2884737; A/C',
                          'VKORC1 QC genotype: 497T>G (5808); chr16:31013055; rs2884737; A/C',
                          'VKORC1 QC genotype: 1173 C>T(6484); chr16:31012379; rs9934438; A/G',
                          'VKORC1 QC genotype: 1542G>C (6853); chr16:31012010; rs8050894; C/G', 
                          'VKORC1 QC genotype: 3730 G>A (9041); chr16:31009822; rs7294;  A/G', 
                          'VKORC1 genotype: 2255C>T (7566); chr16:31011297; rs2359612; A/G',
                          'VKORC1 genotype: 3730 G>A (9041); chr16:31009822; rs7294;  A/G',
                          'VKORC1 QC genotype: 2255C>T (7566); chr16:31011297; rs2359612; A/G',
                          'VKORC1 genotype: -4451 C>A (861); Chr16:31018002; rs17880887; A/C',
                          'VKORC1 QC genotype: -4451 C>A (861); Chr16:31018002; rs17880887; A/C',
                          'VKORC1 genotype: 1173 C>T(6484); chr16:31012379; rs9934438; A/G',
                          'VKORC1 genotype: 1542G>C (6853); chr16:31012010; rs8050894; C/G',
                          'VKORC1 -4451 consensus',
                          'VKORC1 2255 consensus',
                          'VKORC1 497 consensus',
                          'VKORC1 3730 consensus',
                          'VKORC1 1173 consensus',
                          'VKORC1 1542 consensus',
                          'CYP2C9 consensus',
                          'VKORC1 -1639 consensus',
                          'Was Dose of Acetaminophen or Paracetamol (Tylenol) >1300mg/day',
                          'Herbal Medications, Vitamins, Supplements'],errors='ignore')
    df.columns=(
        df.columns.str.strip().str.lower().str.replace(" ","_").str.replace("(","").str.replace(")","").str.replace(">","_").str.replace("/","_").str.replace(",","_")
    )
    column_mapping = {
       "vkorc1_genotype:_-1639_g_a_3673;_chr16:31015190;_rs9923231;_c_t": "vkorc1_1639",
       "anti-fungal_azoles" : "anti_fungal_azoles"
       
}

    df = df.rename(columns=column_mapping)
    return df