import pandas as pd

df = pd.read_csv('mentor-feedback.csv') # https://stats.boloapi.in/question/1964
mentor_mentee_relation = pd.DataFrame(dict())
for i, row in df.groupby('Video Sessions One To One → Booked With ID'):
    for j, row2 in row.groupby('Feedback Feedback Form User Mapping - Feedback Form User Mapping → Filled By ID'):
        feedback = row2['Feedback Feedback Answer - Feedback Answer → Text']
        thumbs_up = feedback[feedback == 'thumbs up'].shape[0]
        thumbs_down = feedback[feedback == 'thumbs down'].shape[0]
        dc = {"student_id": j, "mentor_id": i, "student_name": row2['Auth User - Filled By → Username'].values[0],
               "mentor_name": row['Auth User - Booked With → Username'].values[0], "thumbs_up_count": thumbs_up,
               "thumbs_down_count": thumbs_down}
        mentor_mentee_relation = mentor_mentee_relation.append(dc, ignore_index=True)
mentor_mentee_relation.to_csv('mentor_mentee_relation.csv', index=False)