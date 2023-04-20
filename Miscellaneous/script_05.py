#----------------------------------------------------------------------------------------------------------------------
# Training - Processing General GNC-A Products With Python - Demonstration: NOAA Ocean Color - NetCDF
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
file = Dataset("Samples//VR1VCW_C2021187_C39_153120_165931-171344_184032-185444_202130-203418_220230-220937_VY00_edgemask_chlora.nc")

# Select the extent [min. lon, min. lat, max. lon, max. lat]
#extent = [-120.0, 0.0, -60.0, 44.0] # Full Eastern Caribbean Region (VY)
extent = [-70.0, 10.0, -60.0, 20.0] # Subregion of the Full Eastern Caribbean Region (WY)

# Reading lats and lons 
lats = file.variables['rows'][:]
lons = file.variables['cols'][:]
 
# Latitude lower and upper index
latli = np.argmin( np.abs( lats - extent[1] ) )
latui = np.argmin( np.abs( lats - extent[3] ) )
 
# Longitude lower and upper index
lonli = np.argmin( np.abs( lons - extent[0] ) )
lonui = np.argmin( np.abs( lons - extent[2] ) )
 
# Extract the Ocean Color
data = file.variables['chlor_a'][ : , : , latui:latli , lonli:lonui ]

# Return a reshaped matrix
data = data.squeeze()

#------------------------------------------------------------------------------------------------------

# Getting the file time and date
add_seconds = int(file.variables['time'][0])
date = datetime(1970,1,1,12) + timedelta(seconds=add_seconds)
date_formatted = date.strftime('%Y-%m-%d')

# Print the formatted time and date
print("Ocean Color File Date: ", date_formatted)

#------------------------------------------------------------------------------------------------------

# Choose the plot size (width x height, in inches)
plt.figure(figsize=(10,10))

# Use the Mercator projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# Define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# Create a custom color scale:
colors = ["#84007c", "#1d00e1", "#0066ff", "#00ffe7", "#00ff00", "#ffff00", 
          "#ff8a00", "#ff0000", "#bb0000", "#b46464"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
cmap.set_over('#b46464')
cmap.set_under('#84007c')
vmin = 0.01
vmax = 65.00
    
# Add some various map elements to the plot to make it recognizable.
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN, facecolor='black')

# Plot the image
from matplotlib import colors, cm
norm = colors.LogNorm(vmin, vmax, clip='False')
img = ax.imshow(data, norm=norm,origin='upper', extent=img_extent, cmap=cmap)

# Add a shapefile
shapefile = list(shpreader.Reader('ne_10m_admin_1_states_provinces.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='gray',facecolor='none', linewidth=0.3)

# Add coastlines, borders and gridlines
ax.coastlines(resolution='10m', color='black', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 1), ylocs=np.arange(-90, 90, 1), draw_labels=True)
gl.top_labels = False
gl.right_labels = False

# Add a colorbar
from matplotlib.ticker import LogFormatter
formatter = LogFormatter(10, labelOnlyBase=False) 
plt.colorbar(img, label='Chlorophyll-a (mg/m³)', extend='both', orientation='horizontal', pad=0.05, fraction=0.05, format=formatter)

#ticks = [0.01, 0.1, 0.0, 10, 20]
#plt.colorbar(img, label='Chlorophyll-a (mg/m³)', extend='both', orientation='horizontal', pad=0.03, fraction=0.05)

# Add a title
plt.title('NOAA-20 - VIIRS Chlorophyll Concentration (Chl-a) 750 m ' + date_formatted, fontweight='bold', fontsize=6, loc='left')
plt.title('Region: ' + str(extent), fontsize=6, loc='right')

#------------------------------------------------------------------------------------------------------

# Show the image
plt.show()