from slack_api_functions import SlackAPIFunctions
import pandas as pd


def get_username(name):
    try:
        return name.split("@")[0]
    except:
        return ""

slack_api = SlackAPIFunctions()
df = pd.read_csv('new_users.csv')
all_users = slack_api.get_all_users_list()
df['username'] = df['Slack'].apply(lambda x: get_username(x))
for i, row in df.groupby('Channel_Id'):
    print(i)
    batch_users = row['username'].unique()
    users_id_to_add = all_users[all_users['name'].isin(batch_users)]['id'].tolist()
    slack_api.add_users_in_channel(i, users_id_to_add)