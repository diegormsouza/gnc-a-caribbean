#-----------------------------------------------------------------------------------------------------------
# Training - Processing General GNC-A Products With Python - Demonstration: NOAA Coral Reef Watch 5 km SST - NetCDF
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
file = Dataset("Samples//coraltemp_v3.1_20210706.nc")

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
 
# Extract the Sea Surface Temperature
data = file.variables['analysed_sst'][ 0 , latli:latui , lonli:lonui ]

#------------------------------------------------------------------------------------------------------

# Getting the file time and date
add_seconds = int(file.variables['time'][0])
date = datetime(1981,1,1,12) + timedelta(seconds=add_seconds)
date_formatted = date.strftime('%Y-%m-%d')

# Print the formatted time and date
print("SST File Date: ", date_formatted)

#------------------------------------------------------------------------------------------------------

# Choose the plot size (width x height, in inches)
plt.figure(figsize=(8,6))

# Use the Mercator projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# Define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# Create a custom color scale:
colors = ["#2d001c", "#5b0351", "#780777", "#480a5e", "#1e1552", "#1f337d", 
          "#214c9f", "#2776c6", "#2fa5f1", "#1bad1d", "#8ad900", "#ffec00", 
          "#ffab00", "#f46300", "#de3b00", "#ab1900", "#6b0200"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
cmap.set_over('#6b0200')
cmap.set_under('#2d001c')
vmin = -2.0
vmax = 35.0

# Add some various map elements to the plot to make it recognizable.
ax.add_feature(cfeature.LAND)

# Plot the image
img = ax.imshow(data, vmin=vmin, vmax=vmax, origin='lower', extent=img_extent, cmap=cmap)

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
plt.colorbar(img, label='Sea Surface Temperature (°C)', extend='both', orientation='horizontal', pad=0.05, fraction=0.05)

# Add a title
plt.title('NOAA Coral Reef Watch Daily 5 km SST ' + date_formatted, fontweight='bold', fontsize=8, loc='left')
plt.title('Region: ' + str(extent), fontsize=8, loc='right')

#------------------------------------------------------------------------------------------------------

# Show the image
plt.show()
