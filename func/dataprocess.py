import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

def is_datetime(val):
    try:
        pd.to_datetime(val)
        return True
    except ValueError:
        return False

def preProcess(file_csv):
    df = pd.read_csv(file_csv)
    orig_labels = list(df.columns)
    df.columns = df.iloc[0]
    df = df.reindex(df.index.drop(0))
    new_labels = list(df.columns)

    df = df.set_index('id_person')

    prev_label = ""
    label_groups = {}
    for i in range(0,len(orig_labels)):
        if "Unnamed" not in orig_labels[i]:
            prev_label = orig_labels[i]
            label_groups[prev_label] = []
        label_groups[prev_label].append(new_labels[i])

    label_groups["PESSOA, PIPEDRIVE"].remove("id_person")

    # # Agenda
    # *by PA*
    df = df.dropna(subset=['contract_start_date'])
    df['contract_start_date'] = pd.to_datetime(df['contract_start_date'])
    df['birthdate'] = pd.to_datetime(df['birthdate'])
    df['age_at_subscription'] = df['contract_start_date'] - df['birthdate']
    df['birthdate'] = pd.to_datetime(df['birthdate'])
    df['age_at_subscription'] = df['age_at_subscription'].apply(lambda x: x.days//365.25)
    filterGender = df["id_gender"].isnull()
    df.loc[filterGender, "id_gender"] = 118
    filterMS = df["id_marrital_status"].isna()
    df.loc[filterMS, "id_marrital_status"] = 85
    filterRecon = df["id_person_recommendation"].notna()
    df["id_person_recommendation"] = filterRecon.astype(int)
    df = df.rename(columns={"id_person_recommendation": "was_recommended"})
    filterHealth = df["id_health_plan"].isna()
    df.loc[filterHealth, "id_health_plan"] = 0
    filterHealth = df["id_health_plan"] == 412
    df.loc[filterHealth, "id_health_plan"] = 0
    df.loc[df["id_health_plan"] != 0, "id_health_plan"] = 1
    df = df.rename(columns={"id_health_plan": "private_health_plan"})
    filterCon = df["id_continuity_pf"].notna()
    df["id_continuity_pf"] = filterCon.astype(int)
    df = df.rename(columns={"id_continuity_pf": "has_continuity"})
    filterCanal = df["Canal de Preferência"].isna()
    df.loc[filterCanal, "Canal de Preferência"] = 0 # temporary value
    df = df.drop(columns=["Recebe Comunicados?", "Interesses", "Pontos de Atenção"])

    # # PESSOA, PIPEDRIVE
    # *by Chi*
    lost_time_indices = [i for i, col in enumerate(df.columns) if col == 'lost_time']
    df.iloc[:, lost_time_indices[0]] = df.iloc[:, lost_time_indices[0]].apply(lambda x: x if is_datetime(x) else pd.NaT).replace(to_replace=pd.NaT, value=pd.NaT)
    status_indices = [i for i, col in enumerate(df.columns) if col == 'status']
    df.iloc[:, status_indices[0]] = df.iloc[:, status_indices[0]].replace(to_replace='.*;.*', value=pd.NaT, regex=True)
    df['id_stage'] = df['id_stage'].replace(to_replace='.*;(.*)', value=r'\1', regex=True).str.strip()
    lost_reason_indices = [i for i, col in enumerate(df.columns) if col == 'lost_reason']
    df.iloc[:, lost_reason_indices[0]] = df.iloc[:, lost_reason_indices[0]].replace(to_replace='.*;(.*)', value=r'\1', regex=True).str.strip()
    df["start_of_service"] = df["start_of_service"].apply(lambda x: x if is_datetime(x) else pd.NaT).replace(to_replace='.*;(.*)', value=r'\1', regex=True).str.strip().replace(to_replace=pd.NaT, value=pd.NaT)
    df['id_org'] = df['id_org'].replace(to_replace='.*;(.*)', value=r'\1', regex=True).str.strip()
    df['lost_time_assinatura'] = pd.NaT
    df['lost_time_onboarding'] = pd.NaT
    df['lost_time_assinatura'] = df.iloc[:, lost_time_indices[0]].copy(deep=True)
    df['lost_time_onboarding'] = df.iloc[:, lost_time_indices[1]].copy(deep=True)
    df['status_assinatura'] = pd.NaT
    df['status_onboarding'] = pd.NaT
    df['status_assinatura'] = df.iloc[:, status_indices[0]].copy(deep=True)
    df['status_onboarding'] = df.iloc[:, status_indices[1]].copy(deep=True)
    df['lost_reason_assinatura'] = pd.NaT
    df['lost_reason_onboarding'] = pd.NaT
    df['lost_reason_assinatura'] = df.iloc[:, lost_reason_indices[0]].copy(deep=True)
    df['lost_reason_onboarding'] = df.iloc[:, lost_reason_indices[1]].copy(deep=True)
    df = df.drop(columns=['lost_time', 'status', 'lost_reason'])


    # FUNIL ONBOARDING, PIPEDRIVE 
    # *by Julia*
    df['add_time'].fillna(pd.NaT)
    df['add_time'] = pd.to_datetime(df['add_time'], format='%Y-%m-%d %H:%M:%S')
    status_indices = [i for i, col in enumerate(df.columns) if col == 'status']
    df["status_onboarding"] = df["status_onboarding"].replace('won', 1)
    df["status_onboarding"] = df["status_onboarding"].replace('lost', 0)
    df["status_onboarding"] = df["status_onboarding"].replace('open', pd.NaT) # this is bcuz we dont know if they will churn or not
    df["status_onboarding"].fillna(pd.NaT)
    timedeltas = ["stay_in_pipeline_stages_welcome",
    "stay_in_pipeline_stages_first_meeting",
    "stay_in_pipeline_stages_whoqol"]
    for time in timedeltas:
        df[time] = pd.to_timedelta(df[time]).dt.total_seconds() / 3600
        df[time] = df[time].astype(float)
    df['won_time'] = pd.to_datetime(df['won_time'], format='%Y-%m-%d %H:%M:%S')    
    lost_time_indices = [i for i, col in enumerate(df.columns) if col == 'lost_time']
    df["lost_time_onboarding"] = df["lost_time_onboarding"].apply(lambda x: x if is_datetime(x) else pd.NaT).replace(to_replace=pd.NaT, value=pd.NaT)
    lost_reason_indices = [i for i, col in enumerate(df.columns) if col == 'lost_reason']
    df['activities_count'].fillna(0)
    df['activities_count'] = df['activities_count'].astype('Int64') 

    # ## Agenda
    dates = [x for x in label_groups['ATENDIMENTOS, AGENDA'] if "Datas" in x]
    df[dates[0]] = df[dates[0]].apply(lambda x: x.split(";")[-1] if type(x) == str else "NaT")
    df[dates[0]] = df[dates[0]].apply(lambda x: x[1:] if x[0] == ' ' else x)
    df[dates[0]] = pd.to_datetime(df[dates[0]], format='%Y-%m-%d %H:%M:%S')
    df[dates[1]] = df[dates[1]].apply(lambda x: x.split(";")[-1] if type(x) == str else "NaT")
    df[dates[1]] = df[dates[1]].apply(lambda x: x[1:] if x[0] == ' ' else x)
    df[dates[1]] = pd.to_datetime(df[dates[1]], format='%Y-%m-%d %H:%M:%S')
    df[dates[2]] = pd.to_datetime(df[dates[1]])
    df = df.drop(dates[3], axis=1)
    for label in dates:
        label_groups['ATENDIMENTOS, AGENDA'].remove(label)
    df = df.drop(columns=label_groups["ATENDIMENTOS, AGENDA"][:2])
    df[label_groups["ATENDIMENTOS, AGENDA"][2:4]] = df[label_groups["ATENDIMENTOS, AGENDA"][2:4]].fillna(0)
    df[label_groups["ATENDIMENTOS, AGENDA"][4:6]] = df[label_groups["ATENDIMENTOS, AGENDA"][4:6]].fillna(0)
    df[label_groups["ATENDIMENTOS, AGENDA"][6:8]] = df[label_groups["ATENDIMENTOS, AGENDA"][6:8]].fillna(0)
    df = df.drop(columns=label_groups['ATENDIMENTOS, AGENDA'][8:])

    # # Comunicare
    # *by Barros*
    df[label_groups['COMUNICARE']] = df[label_groups['COMUNICARE']].fillna(0)
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
    for label in list(df[label_groups["WHOQOL"]].columns):
        df[label] = df[label].apply(lambda x: str(x).replace(",",".")).astype(float)

    df[label_groups['WHOQOL']] = df[label_groups['WHOQOL']].astype(float)
    n = ["Mensagens Inbound","Mensagens Outbound", "Ligações Inbound", "Ligações Outbound"]
    df[n] = df[n].fillna(0).astype(int)
    d = ["Data Última Mensagens Inbound", "Data Última Mensagens Outbound", "Data Última Ligações Inbound", "Data Última Ligações Outbound"]
    for date in d:
        df[date] = pd.to_datetime(df[date])

    # ## Cobrança Vindi 
    # *by PA & Julia*
    df['Qde Total de Tentativas de Cobrança'] = df['Qde Total de Tentativas de Cobrança'].fillna(0).astype(int)
    df['Qde Total de Faturas'] = df['Qde Total de Faturas'].fillna(0).astype(int)
    df['faturas_nao_pagas'] = df['Qde Total de Tentativas de Cobrança'] - df['Qde Total de Faturas']
    df = df.drop(columns=['Qde Total de Tentativas de Cobrança', 'Qde Total de Faturas'])
    df = df.drop(columns=['Método de Pagamento', 'Qde Total de Faturas Inadimpletes', 'Qde Perfis de Pagamento Inativos'])
    df['Valor Médio da Mensalidade'] = df['Valor Médio da Mensalidade'].fillna(0).astype(float)
    df['Qde Total de Faturas Pagas após Vencimento'] = df['Qde Total de Faturas Pagas após Vencimento'].fillna(0).astype(int)
    df['Valor Total Inadimplência'] = df['Valor Total Inadimplência'].fillna(0).astype(float)
    df["contract_end_date"] = pd.to_datetime(df["contract_end_date"])
    df["start_of_service"] = pd.to_datetime(df["start_of_service"])
    df["lost_time_assinatura"] = pd.to_datetime(df["lost_time_assinatura"])
    df["lost_time_onboarding"] = pd.to_datetime(df["lost_time_onboarding"])


    to_encode = ["city", "state", "Canal de Preferência", "Problemas Abertos", "status_assinatura", "status_onboarding", "lost_reason_assinatura", "lost_reason_onboarding"]
    encoders = []
    for label in to_encode:
        le = LabelEncoder()
        encoders.append(le)
        df[label] = le.fit_transform(df[label].astype(str))
    to_numeric = to_encode + ["notes_count","done_activities_count","id_stage","id_org","id_marrital_status","private_health_plan","id_gender",
                        "id_label",     
                            ]
    for label in to_numeric:
        df[label] = df[label].astype(float)
    df = df.drop(columns=["postal_code"])
    timedelta = ["stay_in_pipeline_stages_welcome","stay_in_pipeline_stages_first_meeting","stay_in_pipeline_stages_whoqol"]
    for label in timedelta:
        df[label] = pd.to_timedelta(df[label])
    df.to_csv('processed_data.csv')
    df[df["contract_end_date"].notna()].to_csv('processed_data_inactive.csv')
    df[df["contract_end_date"].isna()].to_csv('processed_data_active.csv')

