import pandas as pd

df = pd.read_csv('mock_december.csv') # https://stats.boloapi.in/question/1957
new_df = pd.DataFrame(dict())
for i, row in df.groupby('Auth User - Booked By → Username'):
    Student_rating = 0
    for j, row2 in row.groupby('Technologies Topic Pool - Topic Pool → Title'):
        if j == "DSA Basics 1":
            multiplier = 10
        elif j == "DSA Basics 2":
            multiplier = 15
        elif j == "DSA Basics 3":
            multiplier = 20
        elif j == "DSA Basics 4":
            multiplier = 25
        elif j == "Zenith DSA":
            multiplier = 35
        else:
            multiplier = 10
        for k, row3 in row2.groupby('Video Sessions One Toon Et Oken - One To One Token → Difficulty Level'):
            best_call = row3.sort_values('Final Call')['Final Call'].values[0]
            if best_call == 1:
                multiplier2 = 10
            else:
                best_call = row3.sort_values('Rating', ascending=False)['Final Call'].values[0]
                if best_call == 3:
                    multiplier2 = 7
                else:
                    multiplier2 = 0
            if k == 1:
                multiplier3 = 1
            elif k == 2:
                multiplier3 = 2
            elif k == 3:
                multiplier3 = 4
            elif k == 4:
                multiplier3 = 7
            elif k == 5:
                multiplier3 = 10
            Student_rating += multiplier*multiplier2*multiplier3
    current_course = row['Courses Course - Course → Title'].values[0]
    user_id = row['Booked By ID'].values[0]
    dc = {"username": i, "student_mock_rating": Student_rating, "user_id": user_id, "course": current_course,
          "mock_count": row.shape[0]}
    new_df = new_df.append(dc, ignore_index=True)
new_df.to_csv('mock_rating_december.csv', index=False)