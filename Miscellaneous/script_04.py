#----------------------------------------------------------------------------------------------------------------------
# Training - Processing General GNC-A Products With Python - Demonstration: NOAA Coral Reef Watch 5 km 7-Day SST Trend - NetCDF
# Author: Diego Souza (INPE)
#----------------------------------------------------------------------------------------------------------------------

# Required modules
from netCDF4 import Dataset                 # Read / Write NetCDF4 files
import matplotlib.pyplot as plt             # Plotting library
import cartopy, cartopy.crs as ccrs         # Plot maps
import cartopy.io.shapereader as shpreader  # Import shapefiles
import cartopy.feature as cfeature          # Common drawing and filtering operations
import numpy as np                          # Import the Numpy package
from datetime import datetime, timedelta    # Library to convert julian day to dd-mm-yyyy
import matplotlib.colors                    # Matplotlib colors

#------------------------------------------------------------------------------------------------------

# Open the file using the NetCDF4 library
file = Dataset("Samples//ct5km_sst-trend-7d_v3.1_20210706.nc")

# Select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-100.0, 0.00, -40.00, 40.00]
       
# Reading lats and lons 
lats = file.variables['lat'][:]
lons = file.variables['lon'][:]
 
# Latitude lower and upper index
latli = np.argmin( np.abs( lats - extent[1] ) )
latui = np.argmin( np.abs( lats - extent[3] ) )
 
# Longitude lower and upper index
lonli = np.argmin( np.abs( lons - extent[0] ) )
lonui = np.argmin( np.abs( lons - extent[2] ) )
 
# Extract the 7-Day SST Trend
data = file.variables['trend'][ : , latui:latli , lonli:lonui ]

# Return a reshaped matrix
data = data.squeeze()

#------------------------------------------------------------------------------------------------------

# Getting the file time and date
add_seconds = int(file.variables['time'][0])
date = datetime(1981,1,1,12) + timedelta(seconds=add_seconds)
date_formatted = date.strftime('%Y-%m-%d')

# Print the formatted time and date
print("7-Day SST Trend File Date: ", date_formatted)

#------------------------------------------------------------------------------------------------------

# Choose the plot size (width x height, in inches)
plt.figure(figsize=(8,6))

# Use the Mercator projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# Define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# Create a custom color scale:
colors = ["#640064", "#6300f9", "#2259d3", "#0078ff", "#00bdfe", "#00ffff", 
          "#0ba062", "#ffff00", "#ffbe00", "#ff5000", "#db0000", "#950000", 
          "#640000"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
cmap.set_over('#640000')
cmap.set_under('#640064')
vmin = -3.0
vmax = 3.0

# Add some various map elements to the plot to make it recognizable.
ax.add_feature(cfeature.LAND)

# Plot the image
img = ax.imshow(data, vmin=vmin, vmax=vmax, origin='upper', extent=img_extent, cmap=cmap)

# Add a shapefile
shapefile = list(shpreader.Reader('ne_10m_admin_1_states_provinces.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='gray',facecolor='none', linewidth=0.3)

# Add coastlines, borders and gridlines
ax.coastlines(resolution='10m', color='black', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 10), ylocs=np.arange(-90, 90, 10), draw_labels=True)
gl.top_labels = False
gl.right_labels = False

# Add a colorbar
plt.colorbar(img, label='SST Trend - Past 7 Days (°C/Week)', extend='both', orientation='horizontal', pad=0.05, fraction=0.05)

# Add a title
plt.title('NOAA Coral Reef Watch Daily 5 km SST Trend (Past 7 Days)' + date_formatted, fontweight='bold', fontsize=8, loc='left')
plt.title('Region: ' + str(extent), fontsize=8, loc='right')

#------------------------------------------------------------------------------------------------------

# Show the image
plt.show()
