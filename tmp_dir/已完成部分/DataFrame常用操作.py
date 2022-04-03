import pandas as pd

table = [
    [2.0, 1.0, 3.0],
    [3.0, 1.0, 2.0],
    [1.0, 0.0, 1.0]
]

df = pd.DataFrame(table)
print(df)

new_df = df.cumsum()
print(new_df)
