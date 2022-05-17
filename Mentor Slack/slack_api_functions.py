import requests
import os
from dotenv import load_dotenv
import pandas as pd
from slack_sdk import WebClient
import logging
from datetime import datetime
import re
import gspread
from slack_sdk.errors import SlackApiError


class SlackAPIFunctions:
    def __init__(self):
        self.courses = {"sklkedn8nxy9": "Array", "j294lterlm0f": "Boolean", "yfk0ux5tgdnz": "Char", "h5bcxjg5iyit": "Pointer" , "n16nhsj3qwl9": "Token"}
        self.mentor_channel_identifier = "-mentor-sub-group-"
        self.permanent_members_id = ["U03EHQSN9UM", "U03DYHU8685", "U03ET95U0V9", "U03AHU8JTFZ" , "U03A4ALDY74" , "U03A42G14P8" , "U03ELEXEU4W" , "U038H9F6UMV" , "U03DS3Y8UKX"]

        self.google_authentication_path = "mentor-sheet-2629f5c5388c.json"
        self.google_sheet_name = "Mentor Slack Evaluation: January, 2022"
        self.google_subsheet_name = "Sheet1"

        load_dotenv()
        self.django_token = "BLoBgCTT197RvdNq0CxV8edM2fFSun"
        self.headers = {"Authorization": "Bearer {0}".format(os.getenv("USER_ACCESS_TOKEN"))}
        ACCESS_TOKEN = os.getenv("USER_ACCESS_TOKEN")
        self.client = WebClient(token=ACCESS_TOKEN)
        self.logger = logging.getLogger(__name__)

    def dump_all_channels_list_csv(self):
        channels = pd.DataFrame(dict())
        # channels:read, groups:read, im:read, mpim:read
        url = "https://slack.com/api/conversations.list?types=private_channel&limit=1000"
        result = requests.get(url, headers=self.headers).json()
        for val in result['channels']:
            channels = channels.append(val, ignore_index=True)
        channels.to_csv('private_channels.csv', index=False)
        return channels

    def get_all_users_list(self):
        cursor = True
        count = 1
        users = pd.DataFrame(dict())
        # users:read
        while cursor:
            if not count == 1:
                url = "https://slack.com/api/users.list?pretty=1&cursor={0}%3D".format(next_cursor)
            else:
                url = "https://slack.com/api/users.list?pretty=1"
            response = requests.get(url, headers=self.headers).json()
            next_cursor = response['response_metadata']['next_cursor']
            count += 1
            if next_cursor == "":
                cursor = False
            for val in response['members']:
                val['display_name'] = val['profile']['display_name']
                try:
                    val['email'] = val['profile']['email']
                except:
                    val['email'] = 'slackbot'
                users = users.append(val, ignore_index=True)
        users.to_csv('all_slack_users.csv', index=False)
        return users

    def get_chat_history(self, channel_id):
        # channels:history, groups:history, im:history, mpim:history
        url = "https://slack.com/api/conversations.history?channel={0}".format(channel_id)
        return requests.get(url, headers=self.headers).json()['messages']

    def get_mentors_list(self):
        mappings = pd.DataFrame(dict())
        for course in list(self.courses.keys()):
            url = "https://my.newtonschool.co/api/v1/success_champion/course/h/{0}/sub_batch/list/?offset=0&limit=100&full_info=true".format(
                course)
            headers = {"Authorization": "Bearer {}".format(self.django_token)}
            for sub_batch in requests.get(url, headers=headers).json()['results']:
                try:
                    mentor = sub_batch['course_mentor_mappings'][0]['mentor']['user']['username']
                    name = sub_batch['course_mentor_mappings'][0]['mentor']['user']['first_name'] + " " + \
                           sub_batch['course_mentor_mappings'][0]['mentor']['user']['last_name']
                except:
                    mentor = ""
                    print("No men")
                for user in sub_batch['course_user_mappings']:
                    mentee = user['user']['username']
                    mappings = mappings.append(
                        {"mentor": mentor, "mentee": mentee, "course": self.courses[course], "Name": name},
                        ignore_index=True)
        mappings.to_csv('mentor_mentee_mappings.csv', index=False)
        return mappings

    def replace_id(self, name, users):
        try:
            name = name.lower()
            return users[users['name'] == name]['id'].values[0]
        except:
            return ""

    def evaluate_mentors(self, no_of_days=30):
        df = pd.DataFrame(dict())
        df_list = list()
        cnt = 0
        mentor_mentee_mappings = self.get_mentors_list()
        users = self.get_all_users_list()
        mentor_mentee_mappings['mentor_slack_id'] = mentor_mentee_mappings['mentor'].apply(
            lambda x: self.replace_id(x, users))
        mentor_mentee_mappings['student_slack_id'] = mentor_mentee_mappings['mentee'].apply(
            lambda x: self.replace_id(x, users))
        all_mentors = mentor_mentee_mappings['mentor_slack_id'].unique()
        current_timestamp = datetime.now()
        channels = self.dump_all_channels_list_csv()

        for val in channels:
            if self.mentor_channel_identifier in val['name']:
                total_message_count = 0
                mentor_message_count = 0
                mentor_tagged_count = 0
                chat_history = self.get_chat_history(val['id'])
                for message in chat_history:
                    text = message['text']
                    days = (current_timestamp - datetime.fromtimestamp(int(message['ts'].split(".")[0]))).days
                    if days < no_of_days:
                        if not "has joined the channel" in text:
                            total_message_count += 1
                            try:
                                user = users[users['id'] == message['user']]['real_name'].values[0].split(" ")[
                                    0].lower()
                            except:
                                print(val, message)
                                user = "bot"
                            if user in val['name']:
                                mentor_message_count += 1
                            user_tagged = re.findall("\<(.*?)\>", text)
                            for bbl in user_tagged:
                                bbl = bbl.replace("@", "")
                                if bbl in all_mentors:
                                    mentor_tagged_count += 1
                dct = {"channel_name": val['name'], "total_messages_count": total_message_count,
                       "mentor_message_count": mentor_message_count,
                       "mentor_tagged_count": mentor_tagged_count, "date": current_timestamp}
                df = df.append(dct, ignore_index=True)
                df_list.append({'range': cnt, 'values': [
                    [val['name'], total_message_count, mentor_message_count, mentor_tagged_count,
                     str(current_timestamp)]]})
                cnt += 1
        return df_list

    def mentors_performance_to_sheet(self):
        df = self.evaluate_mentors()
        sa = gspread.service_account(filename=self.google_authentication_path)
        sh = sa.open(self.google_sheet_name)
        wks = sh.worksheet(self.google_subsheet_name)
        length = len(wks.get_all_values())
        for i, val in enumerate(df):
            df[i]['range'] = 'A%s' % (val['range'] + length + 1)
        wks.batch_update(df)

    def add_users_in_channel(self, channel_id, user_ids):
        # channels:write, groups:write, im:write, mpim:write
        try:
            result = self.client.conversations_invite(
                channel=channel_id, users=user_ids
            )
            self.logger.info(result)

        except SlackApiError as e:
            self.logger.error("Error adding user: {}".format(e))

    def create_single_channel(self, channel_name, is_private=False):
        # channels:write, groups:write, im:write, mpim:write
        url = "https://slack.com/api/conversations.create?name={0}&is_private=True".format(channel_name)
        req = requests.get(url, headers=self.headers).json()
        return req

    def create_mentor_channels(self):
        mentor_mentee_mappings = self.get_mentors_list()
        users = self.get_all_users_list()
        mentor_mentee_mappings['mentor_slack_id'] = mentor_mentee_mappings['mentor'].apply(
            lambda x: self.replace_id(x, users))
        mentor_mentee_mappings['student_slack_id'] = mentor_mentee_mappings['mentee'].apply(
            lambda x: self.replace_id(x, users))

        mentor_mentee_mappings['Name'] = mentor_mentee_mappings['Name'].apply(lambda x: x.lower())
        for i, row in mentor_mentee_mappings.groupby('Name'):
            batch = row['course'].values[0].lower()
            mentor_name = i.replace(" ", "-")
            channel_name = batch + self.mentor_channel_identifier + mentor_name
            users = list(row['student_slack_id'].unique())
            mentor_id = list(row['mentor_slack_id'].unique())
            perm = self.permanent_members_id
            try:
                channel_id = self.create_single_channel(channel_name)['channel']['id']
                users_to_add = users + mentor_id + perm
                str_user = ",".join(users_to_add)
                str_user = str_user.replace(",,", ",")
                self.add_users_in_channel(channel_id, str_user)
            except:
                print("mentor_channel_not_created", channel_name)

    def post_a_message(self, channel_id, text):
        # chat:write, chat:write:user, chat:write:bot
        url = "https://slack.com/api/chat.postMessage?channel={0}&text={1}".format(channel_id, text)
        return requests.get(url, headers=self.headers).json()

    def archive_mentor_channels(self):
        # channels:write, groups:write, im:write, mpim:write
        channels = self.dump_all_channels_list_csv()
        for i, row in channels['name'].iteritems():
            if self.mentor_channel_identifier in row:
                url = "https://slack.com/api/conversations.archive?channel={0}".format(channels.loc[i]['id'])
                requests.post(url, headers=self.headers)

    def pin_a_message(self, channel_id, ts):
        # pins:write
        url = "https://slack.com/api/pins.add?channel={0}&timestamp={1}".format(channel_id, ts)
        return requests.get(url, headers=self.headers).json()

    def send_message_to_all_mentor_groups(self):
        channels = self.dump_all_channels_list_csv()
        text = "<!channel> This is your permanent Mentor-Mentee Sub-Group, " \
               "Please get to know each other.\nSchedule for mentor session:\n1. " \
               "There will be 2 Group Sessions of 1.5 hours each week\n2. " \
               "1-1 of 30 minutes with each of you.\n\nNow on, please use only this group for " \
               "any queries related to session scheduling and requesting everybody not to create " \
               "any noise on the main group regarding it.\nMentors are requested to post each week's " \
               "agenda in this channel only.\n\n I hope you all actively engage in conversations and " \
               "build a great community together. Wish you ALL THE LUCK.\n\nAcknowledge with message " \
               "with a :thumbsup: if you're aligned"
        for i, row in channels['name'].iteritems():
            if self.mentor_channel_identifier in row:
                ts = self.post_a_message(channels.loc[i]['id'], text)['ts']
                self.pin_a_message(channels.loc[i]['id'], ts)

    def remove_single_user(self, team_id, user_id):
        # admin.users:write
        url = "https://slack.com/api/admin.users.remove?team_id={0}&user_id={1}".format(team_id, user_id)
        return requests.get(url, headers=self.headers).json()
