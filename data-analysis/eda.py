import pandas as pd

df = pd.read_json("manipulational_conversation.jsonl", lines=True)

print("Dataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nManipulation counts:")
print(df["is_manipulation"].value_counts())

print("\nManipulation types:")
print(df["manipulation_type"].value_counts())

print("\nContext types:")
print(df["context_type"].value_counts())
print("\nAll columns:")
for column in df.columns:
    print(column)

print("\nExample full record:")
print(df.iloc[0].to_dict())