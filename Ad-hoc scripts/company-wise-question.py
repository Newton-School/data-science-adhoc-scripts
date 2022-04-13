import pandas as pd
from collections import Counter

question_df = pd.read_csv('question-tagging.csv').dropna(subset=['Difficulty'])
new_df = pd.DataFrame(dict())
for i, row in question_df.groupby('Company Title'):
    dc = {"company_id": row['Company ID'].values[0], "company_name": i,
          "difficulty-1": Counter(row['Difficulty'].tolist()).most_common(1)[-1][0],
          "difficulty-2": Counter(row['Difficulty'].tolist()).most_common(2)[-1][0],
          "most-asked-topic": Counter(row['Topic-1'].tolist()).most_common(1)[-1][0],
          "second-most-asked-topic": Counter(row['Topic-1'].tolist()).most_common(2)[-1][0],
          "question-type": Counter(row['Theory/Implementation'].tolist()).most_common(1)[-1][0],
          "ctc": row['Min Ctc'].values[0], "number_of_questions": row.shape[0]}
    new_df = new_df.append(dc, ignore_index=True)
new_df.to_csv('company_grouped_questions.csv', index=False)

