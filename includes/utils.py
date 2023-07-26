# for google_sheets.py

def td_group(df):
    td_group = []
    for i in df['TD Score']:
        if not isinstance(i, str):
            if i > 80 and i < 90:
                td_group.append('80-90%')
            elif i > 70 and i <= 80:
                td_group.append('70-80%')
            elif i > 60 and i <= 70:
                td_group.append('60-70%')
            elif i > 50 and i <= 60:
                td_group.append('50-60%')
            elif i <= 50 and i > 0:
                td_group.append('<50%')
            else:
                td_group.append('No Score')
        else:
            td_group.append('No Score')
    return td_group


def calculate_month_weight(df):
    weight_array = []

    for i in range(df.shape[0]):
        weight = df['Disb Value'].iloc[i] / df['Disb Value'][df['Disb month'] == df['Disb month'].iloc[i]].sum()
        weight_array.append(weight)

    return weight_array

