import geopandas as gpd
import pandas as pd
import numpy as np

neighbourhoods = gpd.read_file("data/neighbourhoods.geojson")
full_listings = pd.read_csv("data/listings.csv.gz", compression='gzip')

# checking that the two datasets have matching neighbourhood-cities names
mismatches = set(full_listings["neighbourhood_cleansed"]) - set(neighbourhoods["neighbourhood"])

if len(mismatches) != 0:
    print(f"Mismatched Neighbourhoods: {len(mismatches)}")
else: 
    print("All neighbourhoods match")

gdf = gpd.GeoDataFrame(
    full_listings,
    geometry=gpd.points_from_xy(full_listings.longitude, full_listings.latitude),
    crs="EPSG:4326"
)
print(gdf.columns)

listings_gdf_join = gdf.merge(
    neighbourhoods[["neighbourhood", "geometry"]],
    left_on="neighbourhood_cleansed",
    right_on="neighbourhood",
    how="left",
    suffixes=("", "_city")
)

print(listings_gdf_join["geometry_city"].isnull().sum())

# taking most important features according to literature
X_vars = [
"price", # dependent variable
"name",
"geometry",
"room_type",
"property_type",
"accommodates",
"bedrooms",
"number_of_reviews",
"review_scores_rating",
"host_is_superhost",
"neighbourhood_cleansed",
"geometry_city",
]

# missing values
listings_gdf = listings_gdf_join[X_vars].dropna()

# cleaning price
listings_gdf["price"] = listings_gdf["price"].replace('[\$,]', '', regex=True).astype(float)
listings_gdf["log_price"] = np.log(listings_gdf["price"])
pm_gdf = listings_gdf[
    listings_gdf["neighbourhood_cleansed"].str.strip().str.lower() == "palermo"
]

# Convert Booleans to 0/1 for the regression
#pm_gdf['host_is_superhost'] = pm_gdf['host_is_superhost'].map({'t': 1, 'f': 0}).fillna(0)
#pm_gdf['instant_bookable'] = pm_gdf['instant_bookable'].map({'t': 1, 'f': 0}).fillna(0)

# One-hot encode room_type (Standard practice for categorical data)
#room_dummies = pd.get_dummies(pm_gdf['room_type'], prefix='room', drop_first=True)
#pm_gdf = pd.concat([pm_gdf, room_dummies], axis=1)

print(f"Data Preparation Complete. Final Listings Count: {listings_gdf.shape}, variables: {listings_gdf.columns.tolist()}")
print(f"Data Preparation Complete. Final Listings Count for Palermo: {pm_gdf.shape}, variables: {pm_gdf.columns.tolist()}")

__all__ = [
    "neighbourhoods",
    "full_listings",
    "listings_gdf",
    "pm_gdf"]