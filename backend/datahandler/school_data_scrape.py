import pandas as pd
import os

# File paths
input_path = os.path.join("datasets", "all-indian-schools.csv")
output_path = os.path.join("datasets", "karnataka-schools.csv")

# Read the full dataset
df = pd.read_csv(input_path)

# Normalize the 'state' column (strip whitespace and lowercase)
df['state'] = df['state'].str.strip().str.lower()

# Filter only Karnataka data
karnataka_df = df[df['state'] == 'karnataka'].copy()

# Reset serial_no from 1 to n
karnataka_df['serial_no'] = range(1, len(karnataka_df) + 1)

# Save to new CSV
karnataka_df.to_csv(output_path, index=False)

print(f"Filtered Karnataka data saved to: {output_path}")
