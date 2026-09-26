import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("cleaned_manipulation_data.csv")

print("Dataset Shape:", df.shape)

# 1. Manipulation vs Non-Manipulation
manipulation_counts = df["is_manipulation"].value_counts()

print("\nManipulation vs Non-Manipulation:")
print(manipulation_counts)

manipulation_counts.plot(kind="bar")
plt.title("Manipulation vs Non-Manipulation")
plt.xlabel("Is Manipulation")
plt.ylabel("Number of Conversations")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("manipulation_distribution.png")
plt.show()


# 2. Manipulation Types
type_counts = df["manipulation_type"].value_counts()

print("\nManipulation Types:")
print(type_counts)

type_counts.plot(kind="bar")
plt.title("Distribution of Manipulation Types")
plt.xlabel("Manipulation Type")
plt.ylabel("Number of Conversations")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("manipulation_types.png")
plt.show()


# 3. Context Types
context_counts = df["context_type"].value_counts()

print("\nContext Types:")
print(context_counts)

context_counts.plot(kind="bar")
plt.title("Distribution of Context Types")
plt.xlabel("Context")
plt.ylabel("Number of Conversations")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("context_types.png")
plt.show()


# 4. Manipulation Type by Context
context_manipulation = pd.crosstab(
    df["context_type"],
    df["manipulation_type"]
)

print("\nManipulation Type by Context:")
print(context_manipulation)

context_manipulation.plot(kind="bar", figsize=(10, 6))
plt.title("Manipulation Types Across Different Contexts")
plt.xlabel("Context")
plt.ylabel("Number of Conversations")
plt.xticks(rotation=0)
plt.legend(title="Manipulation Type")
plt.tight_layout()
plt.savefig("manipulation_by_context.png")
plt.show()