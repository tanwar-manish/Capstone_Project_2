import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('myntra_data.csv')
df['price'] = pd.to_numeric(df['price'], errors='coerce')  # Convert price to numeric, set errors to NaN
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')  # Convert rating to numeric

# Handle missing values
df['price'].fillna(df['price'].median(), inplace=True)  # Replace missing prices with median price
df['rating'].fillna(df['rating'].mean(), inplace=True)  # Replace missing ratings with average rating

# Save cleaned data
df.to_csv('myntra_data_cleaned.csv', index=False)



#plot part 

df = pd.read_csv('myntra_data_cleaned.csv')

# # Price distribution
# plt.figure(figsize=(10, 6))
# sns.histplot(df['price'], kde=True)
# plt.title('Price Distribution')
# plt.xlabel('Price')
# plt.ylabel('Frequency')
# plt.show()

# Average rating per brand
plt.figure(figsize=(12, 8))
avg_rating = df.groupby('brand')['rating'].mean().sort_values(ascending=False)
sns.barplot(x=avg_rating.values, y=avg_rating.index)
plt.title('Average Rating per Brand')
plt.xlabel('Average Rating')
plt.ylabel('Brand')
plt.show()
