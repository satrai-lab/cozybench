import numpy as np
import pandas as pd


# Sample dataset of historical thermal sensation records
# Assume the dataset is a pandas DataFrame with columns 'temperature' and 'comfort_level'
# Example: df = pd.DataFrame({'temperature': [...], 'comfort_level': [...]})

def calculate_target_temperature(df, T_current, C_current):
    # Step 1: Extract comfort levels within the temperature range of T_current ± 1°C
    temp_range_df = df[(df['temperature'] >= T_current - 1) & (df['temperature'] <= T_current + 1)]

    if temp_range_df.empty:
        raise ValueError("No data available in the specified temperature range.")

    comfort_levels = temp_range_df['comfort_level']

    # Step 2: Calculate mean (μ) and standard deviation (σ) of the comfort levels
    mu = comfort_levels.mean()
    sigma = comfort_levels.std()

    # Step 3: Determine the position y in the Gaussian distribution for the current comfort level
    y = (C_current - mu) / sigma

    # Step 4: Find the subset of data where users reported being comfortable (e.g., -0.5 ≤ sensation ≤ 0.5)
    comfortable_df = df[(df['comfort_level'] >= -0.5) & (df['comfort_level'] <= 0.5)]

    if comfortable_df.empty:
        raise ValueError("No comfortable data available in the dataset.")

    # Map the y value to a position within the comfortable_df
    comfortable_temperatures = comfortable_df['temperature'].values
    comfortable_comfort_levels = comfortable_df['comfort_level'].values

    # Normalize the comfortable comfort levels to find the target position
    normalized_comfort_levels = (
                                            comfortable_comfort_levels - comfortable_comfort_levels.mean()) / comfortable_comfort_levels.std()

    # Find the temperature that corresponds to the y position
    # We use interpolation to map the y value to the corresponding temperature
    target_temperature = np.interp(y, normalized_comfort_levels, comfortable_temperatures)

    return target_temperature


# Example usage
df = pd.DataFrame({
    'temperature': [22, 23, 24, 25, 26, 23, 24, 22, 21, 25],
    'comfort_level': [-0.5, 0, 0.5, -0.5, 1, -1, 0, -0.5, 0.5, 0]
})

T_current = 24
C_current = 0

try:
    T_target = calculate_target_temperature(df, T_current, C_current)
    print(f"The target temperature for optimal comfort is: {T_target}°C")
except ValueError as e:
    print(e)
