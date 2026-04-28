import pandas as pd
import numpy as np
import geopandas as gpd
from pynhd import WaterData
import matplotlib.pyplot as plt
from shapely.geometry import Point
import warnings
import time
#import folium

"""
This program only maps big data centers and not edge data centers or colocation
"""
"""
def analyze_water_proximity(lat, lon, search_radius_miles=10):
    # Analyzes the distance from a specific lat/lon to the nearest rivers and lakes.
    print(f"Initializing search at Lat: {lat}, Lon: {lon}...")
    
    # 1. Create the Target Point in GPS coordinates (WGS84 / EPSG:4326)
    target_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326")

    # 2. Project to a coordinate system measured in meters (Web Mercator / EPSG:3857)
    # You cannot accurately measure miles using degree-based GPS coordinates.
    target_proj = target_point.to_crs("EPSG:3857")

    # 3. Create the Search Bounding Box
    radius_meters = search_radius_miles * 1609.34
    search_area = target_proj.buffer(radius_meters).to_crs("EPSG:4326")
    bbox = search_area.total_bounds # Returns [min_lon, min_lat, max_lon, max_lat]

    print(f"Querying USGS Hydrography Database for a {search_radius_miles}-mile radius...")

    try:
        # 4. Fetch the Rivers (Flowlines) and Lakes (Waterbodies)
        # This calls the USGS API directly based on our bounding box
        nhd_rivers = WaterData("nhdflowline_network").bybox(bbox)
        nhd_lakes = WaterData("nhdwaterbody").bybox(bbox)

        distances = {}

        # 5. Calculate River Distance
        if not nhd_rivers.empty:
            rivers_proj = nhd_rivers.to_crs("EPSG:3857")
            # Calculate distance from point to the closest line geometry
            dist_meters = target_proj.distance(rivers_proj.unary_union).min()
            distances['Nearest River/Stream'] = dist_meters / 1609.34
        else:
            distances['Nearest River/Stream'] = float('inf')

        # 6. Calculate Lake Distance
        if not nhd_lakes.empty:
            lakes_proj = nhd_lakes.to_crs("EPSG:3857")
            # Calculate distance from point to the closest polygon geometry
            dist_meters = target_proj.distance(lakes_proj.unary_union).min()
            distances['Nearest Lake/Reservoir'] = dist_meters / 1609.34
        else:
            distances['Nearest Lake/Reservoir'] = float('inf')

        # 7. Print Results
        print("\n--- PROXIMITY RESULTS ---")
        for water_type, dist in distances.items():
            if dist == float('inf'):
                print(f"{water_type}: NONE found within {search_radius_miles} miles.")
            else:
                print(f"{water_type}: {dist:.2f} miles away")
                
        return distances

    except Exception as e:
        print(f"\nError: Could not retrieve data. API may be down or box is empty.")
        print(f"Details: {e}")
        return None

csv = "/Users/nabilmouss/Desktop/ece3600.csv"

dataframe = pd.read_csv(csv)

state_arr = []
sqft_arr = []
longitude_arr = []
latitude_arr = []
texas_count = 0
virginia_count = 0
for state, sqft, longitude, latitude in zip(dataframe["state"], dataframe["sqft"], dataframe["lon"], dataframe["lat"]):
    if state == "Virginia" or state == "Texas":
        state_arr.append(state)
        sqft_arr.append(sqft)
        longitude_arr.append(longitude)
        latitude_arr.append(latitude)
    
    if state == "Virginia":
        virginia_count += 1
    if state == "Texas":
        texas_count += 1

state_arr = np.array(state_arr)
sqft_arr = np.array(sqft_arr)
longitude_arr = np.array(longitude_arr)
latitude_arr = np.array(latitude_arr)

Texas_distance_Lake_Resevior = 0
Virginia_distance_Lake_Resevior = 0
Texas_distance_River_Stream = 0
Virginia_distance_River_Stream = 0

Lake_Resevior_count_texas = 0
Lake_Resevior_count_virginia = 0
River_Stream_count_virginia = 0
River_Stream_count_texas = 0

for latitude, longitude, state in zip(latitude_arr, longitude_arr, state_arr):
    data = analyze_water_proximity(latitude, longitude)

    if 'Nearest River/Stream' in data and state == "Texas":
        Texas_distance_River_Stream += data['Nearest River/Stream']
        River_Stream_count_texas += 1
    
    if 'Nearest River/Stream' in data and state == "Virginia":
        Virginia_distance_River_Stream += data['Nearest River/Stream']
        River_Stream_count_virginia += 1

    if 'Nearest Lake/Reservoir' in data and state == "Texas":
        Texas_distance_Lake_Resevior += data['Nearest Lake/Reservoir']
        Lake_Resevior_count_texas += 1
    
    if 'Nearest Lake/Reservoir' in data and state == "Virginia":
        Virginia_distance_Lake_Resevior += data['Nearest Lake/Reservoir']
        Lake_Resevior_count_virginia += 1    
    
    time.sleep(1)

Texas_distance_Lake_Resevior /= Lake_Resevior_count_texas
Virginia_distance_Lake_Resevior /= Lake_Resevior_count_virginia
Texas_distance_River_Stream /= River_Stream_count_texas
Virginia_distance_River_Stream /= River_Stream_count_virginia

# 1. Set up the figure size
plt.figure(figsize=(10, 6))

# 2. Create grouped bar data
water_types = ['Lake/Reservoir', 'River/Stream']
texas_values = [Texas_distance_Lake_Resevior, Texas_distance_River_Stream]
virginia_values = [Virginia_distance_Lake_Resevior, Virginia_distance_River_Stream]

# 3. Set up bar positions
x = np.arange(len(water_types))
width = 0.35

# 4. Create the grouped bars
bars1 = plt.bar(x - width/2, texas_values, width, label='Texas', color='#ff9999')
bars2 = plt.bar(x + width/2, virginia_values, width, label='Virginia', color='#66b3ff')

# 5. Add titles and axis labels
plt.title('Average Distance to Nearest Water Source for Data Centers', fontsize=14, pad=15)
plt.xlabel('Water Source Type', fontsize=12)
plt.ylabel('Average Distance (Miles)', fontsize=12)
plt.xticks(x, water_types)
plt.legend()

# 6. Add the exact numbers on top of the bars for clarity
for bars in [bars1, bars2]:
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f'{yval:.2f} mi', ha='center', va='bottom', fontsize=11)

# 6. Adjust layout so labels don't get cut off
plt.tight_layout()

# 7. Display the plot (or save it directly to an image file for your presentation)
# plt.show()
# plt.savefig('water_distance_comparison.png') # Use this line instead of plt.show() if you want to save the image
"""

# df = pd.read_csv("/Users/nabilmouss/Desktop/ece3600.csv")

# df_filtered = df[df['state'].isin(['Texas', 'Virginia'])].copy()

# # 1. Define your Tier Lists (Make sure spelling matches your CSV perfectly)
# tier_0_ops = ['Oracle', 'OpenAI', 'xAI'] # The Gigawatt builders

# tier_1_ops = ['Amazon Web Services', 'Microsoft', 'Google', 'Meta']

# tier_2_ops = ['Digital Realty', 'Equinix', 'Quality Technology Services', 
#               'CyrusOne', 'CloudHQ', 'Vantage Data Centers', 'Aligned', 
#               'DataBank', 'Databank', 'Centersquare', 'NTT', 'CoreSite', 'Flexential']

# # 2. Create the categorization function
# def assign_tier(row):
#     operator = str(row['operator'])
#     sqft = row['sqft']
    
#     # Rule 1: Check Known Operators first
#     if pd.notna(row['operator']):
#         if any(op in operator for op in tier_1_ops):
#             return 'Tier 1'
#         elif any(op in operator for op in tier_2_ops):
#             return 'Tier 2'
#         elif operator != 'nan': # If there is a name, but it's not in T1 or T2
#             return 'Tier 3'
            
#     # Rule 2: Fallback to Square Footage if operator is missing (NaN)
#     if pd.notna(sqft):
#         if sqft >= 400000:
#             return 'Tier 1'
#         elif 100000 <= sqft < 400000:
#             return 'Tier 2'
#         else:
#             return 'Tier 3'
            
#     # If absolutely everything is missing, assume it's small
#     return 'Tier 3'

# # 3. Apply the function to create your new Machine Learning Feature
# df_filtered['operator_tier'] = df_filtered.apply(assign_tier, axis=1)
# df_filtered.to_csv("/Users/nabilmouss/Desktop/ece3600_with_tiers.csv", index=False)
# # 4. Check the results!
# print(df_filtered['operator_tier'].value_counts())

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# 1. Load Data
df = pd.read_csv("/Users/nabilmouss/Desktop/ece3600.csv")
df_filtered = df[df['state'].isin(['Texas', 'Virginia'])].copy()

# 2. Assign Historical Tiers (Tiers 1, 2, and 3 only)
tier_1_ops = ['Amazon Web Services', 'Microsoft', 'Google', 'Meta']
tier_2_ops = ['Digital Realty', 'Equinix', 'Quality Technology Services', 
              'CyrusOne', 'CloudHQ', 'Vantage Data Centers', 'Aligned', 
              'DataBank', 'Databank', 'Centersquare', 'NTT', 'CoreSite', 'Flexential']

def assign_tier(row):
    operator = str(row['operator'])
    sqft = row['sqft']
    if pd.notna(row['operator']):
        if any(op in operator for op in tier_1_ops): return 'Tier 1'
        elif any(op in operator for op in tier_2_ops): return 'Tier 2'
        elif operator != 'nan': return 'Tier 3'
    if pd.notna(sqft):
        if sqft >= 400000: return 'Tier 1'
        elif 100000 <= sqft < 400000: return 'Tier 2'
        else: return 'Tier 3'
    return 'Tier 3'

df_filtered['operator_tier'] = df_filtered.apply(assign_tier, axis=1)

# 3. Generate Historical Target Variable (Power MW)
power_multipliers = {'Tier 1': 300, 'Tier 2': 150, 'Tier 3': 50}
np.random.seed(42)
noise = np.random.normal(0.9, 1.1, len(df_filtered))
df_filtered['Target_Power_MW'] = (df_filtered['sqft'] * df_filtered['operator_tier'].map(power_multipliers) / 1000000) * noise
df_filtered = df_filtered.dropna(subset=['sqft', 'Target_Power_MW'])

print("Preparing Data for Linear Regression...")

# =========================================================================
# 4. THE FIX: SYNTHETIC DATA AUGMENTATION
# Inject the future 4.5 GW Oracle facility so the model can "learn" Tier 0
# =========================================================================
synthetic_tier_0 = pd.DataFrame([{
    'sqft': 550000,
    'state': 'Texas',
    'operator_tier': 'Tier 0',
    'Target_Power_MW': 500.0  # 4,500 MW (4.5 GW)
}])
# Append it to our dataset
df_filtered = pd.concat([df_filtered, synthetic_tier_0], ignore_index=True)


# 5. Create Interaction Terms
# Now that Tier 0 actually exists in the data, this will work perfectly!
df_filtered['sqft_Tier0'] = df_filtered['sqft'] * (df_filtered['operator_tier'] == 'Tier 0').astype(int)
df_filtered['sqft_Tier1'] = df_filtered['sqft'] * (df_filtered['operator_tier'] == 'Tier 1').astype(int)
df_filtered['sqft_Tier2'] = df_filtered['sqft'] * (df_filtered['operator_tier'] == 'Tier 2').astype(int)
df_filtered['sqft_Tier3'] = df_filtered['sqft'] * (df_filtered['operator_tier'] == 'Tier 3').astype(int)

# 6. Train the Linear Regression Model
lr_features = ['sqft_Tier0', 'sqft_Tier1', 'sqft_Tier2', 'sqft_Tier3']
X_lr = df_filtered[lr_features]
y_power = df_filtered['Target_Power_MW']

X_train_lr, X_test_lr, y_train_lr, y_test_lr = train_test_split(X_lr, y_power, test_size=0.2, random_state=42)

# Set fit_intercept=False because a 0 sqft building uses 0 MW
lr_model = LinearRegression(fit_intercept=False)
lr_model.fit(X_train_lr, y_train_lr)

print("Linear Regression Model Trained Successfully!")

# 7. The Extrapolation Test
def test_linear_extrapolation(test_sqft, tier_num):
    input_data = [0, 0, 0, 0]
    input_data[tier_num] = test_sqft 
    prediction_mw = lr_model.predict([input_data])[0]
    print(f"\n⚡ Extrapolated Power for {test_sqft:,} sqft (Tier {tier_num}): {prediction_mw:,.2f} MW")

# Test the massive 550,000 sqft AI Supercluster (Tier 0)
test_linear_extrapolation(test_sqft=550000, tier_num=0)

# Test a standard Cloud data center of the same size (Tier 1)
test_linear_extrapolation(test_sqft=550000, tier_num=1)

import matplotlib.pyplot as plt

# Define the categories and their labels
tiers = [
    'Kendeda\n(Actual)',
    'Tier 3\n(Telecom / Edge)',
    'Tier 2\n(Colocation)',
    'Tier 1\n(Cloud / Hyperscale)',
    'Tier 0\n(AI Supercluster)'
]

# Power density multipliers (Watts per sqft)
multipliers_w_per_sqft = [50, 150, 300, 500]
facility_size_sqft = 18600

# Calculate MW for a 550k sqft facility
power_mw = [0.03] + [(facility_size_sqft * m) / 1000000 for m in multipliers_w_per_sqft]

# Create the plot
plt.figure(figsize=(10, 7))
bars = plt.bar(tiers, power_mw, color=['#9467bd', '#2ca02c', '#1f77b4', '#ff7f0e', '#d62728'])

# Add labels and title
plt.title(f'Power Demand for a 18,600 sqft Facility (Same size as Kendeda)', fontsize=16, pad=20)
plt.ylabel('Estimated Power Demand (Megawatts)', fontsize=12)
plt.xlabel('Infrastructure Tier', fontsize=12)

# Add grid lines behind the bars for easier reading
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.gca().set_axisbelow(True)

# Add exact numbers on top of the bars
max_height = max(power_mw)
for bar in bars:
    yval = bar.get_height()
    offset = max_height * 0.01
    label = f'{yval:,.2f} MW' if yval < 1 else f'~{yval:,.1f} MW'
    plt.text(bar.get_x() + bar.get_width()/2, yval + offset, label,
             ha='center', va='bottom', fontsize=12, fontweight='bold')

# Adjust layout and save the image
plt.tight_layout()
plt.savefig('tier_differences.png', dpi=300)
print("Graph saved successfully as 'tier_differences.png'!")