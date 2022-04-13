import requests
import pandas as pd

courses = {"858vixlx9sj4": "Zelda", "jkw1sql95rbi": "Mario", "tw8gbvg2bw5a": "Sonic", "350nvj5yy5wq": "Tetris"}
mappings = pd.DataFrame(dict())
for course in list(courses.keys()):
  url = "https://my.newtonschool.co/api/v1/success_champion/course/h/{0}/sub_batch/list/?offset=0&limit=100&full_info=true".format(course)
  headers = {"Authorization": "Bearer pbSgjRcBxtGeki3ChZG8vKbWjdAsBi"}
  for sub_batch in requests.get(url, headers=headers).json()['results']:
    try:
      mentor = sub_batch['course_mentor_mappings'][0]['mentor']['user']['username']
      name = sub_batch['course_mentor_mappings'][0]['mentor']['user']['first_name'] + " " + sub_batch['course_mentor_mappings'][0]['mentor']['user']['last_name']
    except:
      mentor = ""
      print("No men")
    for user in sub_batch['course_user_mappings']:
      mentee = user['user']['username']
      mappings = mappings.append({"mentor": mentor, "mentee": mentee, "course": courses[course], "Name": name}, ignore_index=True)
mappings.to_csv('mentor-mentee-mappings-jan.csv', index=False)