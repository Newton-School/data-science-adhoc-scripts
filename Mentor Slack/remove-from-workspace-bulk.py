import pandas as pd
from slack_api_functions import SlackAPIFunctions

remove_users_df = pd.read_csv('users_to_remove.csv')
all_users = SlackAPIFunctions().get_all_users_list()
team_id = "T039MJ5BJ1E"
for user in remove_users_df['username'].unique():
    try:
        user_id = all_users[all_users['name'] == user]['id'].values[0]
        print(SlackAPIFunctions().remove_single_user(team_id, user_id))
    except:
        print("user_not_found")
