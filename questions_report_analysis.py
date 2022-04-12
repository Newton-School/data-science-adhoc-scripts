import requests
import json
import gspread
import numpy as np

url = "https://slack.com/api/conversations.history?channel=C037JKKRBQ8"
headers = {"Authorization": "Bearer xoxp-1557508101587-2134253533808-3240212146995-b6f9e32b747843a13ce5be6e21aa247d"}
sa = gspread.service_account(filename="C:\\Workspace\\Newton School\\Slack-Automation\\mentor-sheet-2629f5c5388c.json")
sh = sa.open("Assignment Questions Feedback")
wks = sh.worksheet("Sheet1")
df = wks.get_all_values()
timestamps = list()
for val in df[1:]:
    timestamps.append(val[0])
length = len(df)
feedback = ()
final_values = []
for msg in requests.get(url, headers=headers).json()['messages']:
    if "bot_id" in list(msg.keys()):
        try:
            if not msg['ts'] in timestamps:
                text = json.loads(msg['text'])
                playground_hash = text['questionDetails']['questionHash']
                url = "https://my.newtonschool.co/api/v1/playground/coding/h/%s/" % playground_hash
                headers = {"Authorization": "Bearer wpF2n86JigxwdpQayJuHGB2bvcx7Zd"}
                res = requests.get(url, headers=headers).json()
                print(res)
                title = res['assignment_question']['question_title']
                user = res['owners'][0]['username']
                values = [msg['ts'], user, title, "", "", "", "", ""]
                for ran in range(1, 6):
                    if "%s" % ran in text['feedback'].keys():
                        values[ran+2] = True
                final_values.append(values)
        except:
            pass
wks.batch_update([{'range': 'A{0}:L{1}'.format(length+1, length+1+len(final_values)),
                   'values': final_values}])
