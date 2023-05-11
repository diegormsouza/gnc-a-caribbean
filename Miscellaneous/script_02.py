#-----------------------------------------------------------------------------------------------------------
# Training - Processing General GNC-A Products With Python - Demonstration: NOAA Coral Reef Watch 5 km SSTA - NetCDF
# Author: Diego Souza (INPE)
#-----------------------------------------------------------------------------------------------------------

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
file = Dataset("Samples//ct5km_ssta_v3.1_20210706.nc")

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
 
# Extract the SST Anomaly
data = file.variables['sea_surface_temperature_anomaly'][ 0 , latui:latli , lonli:lonui ]

#------------------------------------------------------------------------------------------------------

# Getting the file time and date
add_seconds = int(file.variables['time'][0])
date = datetime(1981,1,1,12) + timedelta(seconds=add_seconds)
date_formatted = date.strftime('%Y-%m-%d')

# Print the formatted time and date
print("SST Anomaly File Date: ", date_formatted)

#------------------------------------------------------------------------------------------------------

# Choose the plot size (width x height, in inches)
plt.figure(figsize=(8,6))

# Use the Mercator projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# Define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# Create a custom color scale:
colors = ["#57004d", "#730069", "#910087", "#2c0699", "#4d32af", 
          "#6b5ac3", "#0004a4", "#0014c0", "#0024dc", "#0043ff",
          "#005fff", "#007bff", "#00a5ff", "#00e1ff", "#ffffff", 
          "#ffffff", "#ffffff", "#f3f000", "#ffd200", "#f0be00",
          "#f0aa00", "#f09600", "#fd7800", "#f56400", "#ef5500", 
          "#fb3000", "#eb1800", "#db0000", "#a02000", "#8a0f00", 
          "#7d0400"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
cmap.set_over('#7d0400')
cmap.set_under('#57004d')
vmin = -5.0
vmax = 5.0

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
plt.colorbar(img, label='SST Anomalies (°C)', extend='both', orientation='horizontal', pad=0.05, fraction=0.05)

# Add a title
plt.title('NOAA Coral Reef Watch Daily 5 km SST Anomalies ' + date_formatted, fontweight='bold', fontsize=8, loc='left')
plt.title('Region: ' + str(extent), fontsize=8, loc='right')

#------------------------------------------------------------------------------------------------------

# Show the image
plt.show()
