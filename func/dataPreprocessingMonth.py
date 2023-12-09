import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np
import warnings
warnings.filterwarnings('ignore')

month = '10'
year = '23'

def is_datetime(val):
    try:
        pd.to_datetime(val)
        return True
    except ValueError:
        return False

def process_csv(csv_file):
    csv = csv_file

    df = pd.read_csv(csv)

    # storing prev labels
    orig_labels = list(df.columns)

    # drop df first row and making the second a new header
    df.columns = df.iloc[0]
    df = df.reindex(df.index.drop(0))
    new_labels = list(df.columns)

    # make id_person take the place of the index
    df = df.set_index('id_person')

    prev_label = ""
    label_groups = {}
    for i in range(0,len(orig_labels)):
        if "Unnamed" not in orig_labels[i]:
            prev_label = orig_labels[i]
            label_groups[prev_label] = []
        label_groups[prev_label].append(new_labels[i])

    label_groups["PESSOA, PIPEDRIVE"].remove("id_person") # removing id_person from the list, so it doesn't try to pull the new index

    df = df.dropna(subset=['contract_start_date'])
    df['contract_start_date'] = pd.to_datetime(df['contract_start_date'])

    df['birthdate'] = pd.to_datetime(df['birthdate'])
    df['age_at_subscription'] = df['contract_start_date'] - df['birthdate']
    df['age_at_subscription'] = df['age_at_subscription'].apply(lambda x: x.days//365.25)

    filterGender = df["id_gender"].isnull()
    # substitute id gender == isNa for 118 rather not say
    df.loc[filterGender, "id_gender"] = 118

    filterMS = df["id_marrital_status"].isna()
    # set values in filter marrital status to 85 "outdated form" or "rather not say"
    df.loc[filterMS, "id_marrital_status"] = 85

    filterRecon = df["id_person_recommendation"].notna()
    df["id_person_recommendation"] = filterRecon.astype(int)
    # rename collumn to was_recommended
    df = df.rename(columns={"id_person_recommendation": "was_recommended"})

    filterHealth = df["id_health_plan"].isna()
    df.loc[filterHealth, "id_health_plan"] = 0

    filterHealth = df["id_health_plan"] == 412
    df.loc[filterHealth, "id_health_plan"] = 0

    df.loc[(df["id_health_plan"] != 0), "id_health_plan"] = 1

    # rename to private_health_plan
    df = df.rename(columns={"id_health_plan": "private_health_plan"})

    filterCon = df["id_continuity_pf"].notna()
    df["id_continuity_pf"] = filterCon.astype(int)
    # rename to has_continuity
    df = df.rename(columns={"id_continuity_pf": "has_continuity"})
    df["has_continuity"].value_counts()

    filterCanal = df["Canal de Preferência"].isna()
    df.loc[filterCanal, "Canal de Preferência"] = 0 # temporary value swap for correspondent value 'rather not say' or 'outdated form'

    ###
    # empty list up to last revisiting
    df = df.drop(columns=["Recebe Comunicados?"])
    df = df.drop(columns=["Interesses"])
    df = df.drop(columns=["Pontos de Atenção"])
    ###

    lost_time_indices = [i for i, col in enumerate(df.columns) if col == 'lost_time']
    #print(df.iloc[:, lost_time_indices[0]].unique())

    # Check if a value is a datetime


    # replace all non-datetime values with NaN
    df.iloc[:, lost_time_indices[0]] = df.iloc[:, lost_time_indices[0]].apply(lambda x: x if is_datetime(x) else pd.NaT).replace(to_replace=pd.NaT, value=pd.NaT)

    status_indices = [i for i, col in enumerate(df.columns) if col == 'status']

    # replace every value with a ";" with NaN
    df.iloc[:, status_indices[0]] = df.iloc[:, status_indices[0]].replace(to_replace='.*;.*', value=pd.NaT, regex=True)

    df['id_stage'] = df['id_stage'].replace(to_replace='.*;(.*)', value=r'\1', regex=True).str.strip()

    lost_reason_indices = [i for i, col in enumerate(df.columns) if col == 'lost_reason']

    # for every item in the column "df.iloc[:, lost_reason_indices[0]]", if it has a ";" only keep the last value. also remove any spaces
    df.iloc[:, lost_reason_indices[0]] = df.iloc[:, lost_reason_indices[0]].replace(to_replace='.*;(.*)', value=r'\1', regex=True).str.strip()

    # replace all non-datetime values in df["start_of_service"] with NaN. also if it has a ";" only keep the last value. also remove any spaces. also replace any NaT with NaN
    df["start_of_service"] = df["start_of_service"].apply(lambda x: x if is_datetime(x) else pd.NaT).replace(to_replace='.*;(.*)', value=r'\1', regex=True).str.strip().replace(to_replace=pd.NaT, value=pd.NaT)

    # create a new column named lost_time_assinatura and one named lost_time_onboarding
    df['lost_time_assinatura'] = pd.NaT
    df['lost_time_onboarding'] = pd.NaT

    # copy the values from df.iloc[:, lost_time_indices[0]] to df['lost_time_assinatura'] and the values from df.iloc[:, lost_time_indices[1]] to df['lost_time_onboarding']
    df['lost_time_assinatura'] = df.iloc[:, lost_time_indices[0]].copy(deep=True)
    df['lost_time_onboarding'] = df.iloc[:, lost_time_indices[1]].copy(deep=True)

    # create a new column named status_assinatura and one named status_onboarding
    df['status_assinatura'] = pd.NaT
    df['status_onboarding'] = pd.NaT

    # copy the values from df.iloc[:, status_indices[0]] to df['status_assinatura'] and the values from df.iloc[:, status_indices[1]] to df['status_onboarding']
    df['status_assinatura'] = df.iloc[:, status_indices[0]].copy(deep=True)
    df['status_onboarding'] = df.iloc[:, status_indices[1]].copy(deep=True)

    # create a new column named lost_reason_assinatura and one named lost_reason_onboarding
    df['lost_reason_assinatura'] = pd.NaT
    df['lost_reason_onboarding'] = pd.NaT

    # copy the values from df.iloc[:, lost_reason_indices[0]] to df['lost_reason_assinatura'] and the values from df.iloc[:, lost_reason_indices[1]] to df['lost_reason_onboarding']
    df['lost_reason_assinatura'] = df.iloc[:, lost_reason_indices[0]].copy(deep=True)
    df['lost_reason_onboarding'] = df.iloc[:, lost_reason_indices[1]].copy(deep=True)

    # remove the unused columns
    df = df.drop(columns=['lost_time', 'status', 'lost_reason'])

    # converts the add_time column to datetime
    df['add_time'] = pd.to_datetime(df['add_time'], format='%Y-%m-%d %H:%M:%S')

    # Same as above, there are two columns with the same name
    status_indices = [i for i, col in enumerate(df.columns) if col == 'status']

    #  replaces 'won' with 1 and 'lost' with 0, and 'open' with NaT
    df["status_onboarding"] = df["status_onboarding"].replace('won', 1)
    df["status_onboarding"] = df["status_onboarding"].replace('lost', 0)
    df["status_onboarding"] = df["status_onboarding"].replace('open', pd.NaT) # this is bcuz we dont know if they will churn or not
    df["status_onboarding"].fillna(pd.NaT)

    # converts them to timedelta
    timedeltas = ["stay_in_pipeline_stages_welcome",
    "stay_in_pipeline_stages_first_meeting",
    "stay_in_pipeline_stages_whoqol"]

    for time in timedeltas:
        # convert to time delta, minutes
        df[time] = pd.to_timedelta(df[time]).dt.total_seconds()/60
        # convert to float
        df[time] = df[time].astype(float)            

    df['won_time'] = pd.to_datetime(df['won_time'], format='%Y-%m-%d %H:%M:%S')  

    df["lost_time_onboarding"] = df["lost_time_onboarding"].apply(lambda x: x if is_datetime(x) else pd.NaT).replace(to_replace=pd.NaT, value=pd.NaT)

    df['activities_count'] = df['activities_count'].astype('Int64')   

    dates = [x for x in label_groups['ATENDIMENTOS, AGENDA'] if "Datas" in x]
    for date in dates:
        df[dates] = df[dates].apply(lambda x: x.split(";")[-1] if type(x) == str else "NaT")
        df[dates] = df[dates].apply(lambda x: x[1:] if x[0] == ' ' else x)

        label_groups['ATENDIMENTOS, AGENDA'].remove(date)

    # do it with apply later
    for label in list(df[label_groups["WHOQOL"][1:]].columns):
        for i in df.index:
            if type(df[label][i]) == str:
                #print(df[label][i])
                if ";" in df[label][i]:
                    l = df[label][i].replace(",",".").split(";")
                    sumV = 0
                    for j in l:
                        sumV += float(j)

                    df.loc[i,label] = sumV/len(l)   
            elif df[label][i] == "nan":
                df.loc[i,label] = int(str(df[label][i]).replace(",","."))

    #replace every "," in df[label_groups['WHOQOL']] with a "."
    for label in list(df[label_groups["WHOQOL"]].columns):
        df[label] = df[label].apply(lambda x: str(x).replace(",",".")).astype(float)

    df[label_groups['WHOQOL']] = df[label_groups['WHOQOL']].astype(float)

    df['Qde Total de Tentativas de Cobrança'] = df['Qde Total de Tentativas de Cobrança'].fillna(0).astype(int)
    df['Qde Total de Faturas'] = df['Qde Total de Faturas'].fillna(0).astype(int)

    df['faturas_nao_pagas'] = df['Qde Total de Tentativas de Cobrança'] - df['Qde Total de Faturas']

    df = df.drop(columns=['Qde Total de Tentativas de Cobrança', 'Qde Total de Faturas'])

    df = df.drop(columns=['Método de Pagamento', 'Qde Total de Faturas Inadimpletes', 'Qde Perfis de Pagamento Inativos'])

    # label encoder state and city
    random_seed = 42
    np.random.seed(random_seed)

    to_encode = ["city", "state", "Canal de Preferência", "Problemas Abertos", "status_assinatura", "status_onboarding", "lost_reason_assinatura", "lost_reason_onboarding"]
    encoders = []
    for label in to_encode:
        df[label] = df[label].fillna(0)
        for i in range(df[label].size):
            if type(df[label][i]) == str:
                summy =  [ord(c) for c in df[label][i]]
                df[label][i] = int(abs(sum(summy) - 2000))
        df[label] = df[label].replace(0, np.nan)

    to_numeric = to_encode + ["notes_count","done_activities_count","id_stage","id_org","id_marrital_status","private_health_plan","id_gender",
                        "id_label",     
                            ]
    for label in to_numeric:
        # if label == id_org
        if label == "id_org":    
            # use last value if divided by ;
            df[label] = df[label].replace(to_replace='.*;(.*)', value=r'\1', regex=True).str.strip()
        else :
            df[label] = df[label].astype(float)

    filterA = df["status_assinatura"] == 2
    df.loc[filterA, "status_assinatura"] = 0
    df["status_assinatura"].value_counts()

    # drop postal code
    df = df.drop(columns=["postal_code"])

    timedelta = ["stay_in_pipeline_stages_welcome","stay_in_pipeline_stages_first_meeting","stay_in_pipeline_stages_whoqol"]
    # change qde prescrições all to 0
    # save as preprocessed_data
    df.to_csv(f'processed_data.csv', index=True)
