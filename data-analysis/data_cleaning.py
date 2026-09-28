import pandas as pd
import re

# Load dataset
df = pd.read_json("manipulational_conversation.jsonl", lines=True)

print("Original shape:", df.shape)

# Check missing values
print("\nMissing values:")
print(df.isnull().sum())

# Check duplicates
print("\nDuplicate conversations:")
print(df.duplicated(subset=["conversation_id"]).sum())


# Combine all messages into one conversation
def combine_messages(messages):
    texts = []

    for message in messages:
        speaker = message["speaker"]
        text = message["text"]

        texts.append(f"{speaker}: {text}")

    return " ".join(texts)


df["conversation_text"] = df["messages"].apply(combine_messages)


# Basic text cleaning
def clean_text(text):
    text = str(text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


df["cleaned_text"] = df["conversation_text"].apply(clean_text)


# Remove duplicate conversations if any
df = df.drop_duplicates(subset=["conversation_id"])


# Remove rows with empty conversation text
df = df[df["cleaned_text"].str.len() > 0]


# Save cleaned dataset
df.to_csv("cleaned_manipulation_data.csv", index=False)


print("\nCleaned shape:", df.shape)

print("\nExample cleaned conversation:")
print(df["cleaned_text"].iloc[0])

print("\nSaved as cleaned_manipulation_data.csv")