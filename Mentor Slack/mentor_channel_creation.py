from slack_api_functions import SlackAPIFunctions

slack_api = SlackAPIFunctions()
#slack_api.archive_mentor_channels()
slack_api.create_mentor_channels()
slack_api.send_message_to_all_mentor_groups()