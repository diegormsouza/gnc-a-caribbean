#-----------------------------------------------------------------------------------------------------------
# Training - Processing General GNC-A Products With Python - Demonstration: Blended Rain Rate - NetCDF
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
name = "BHP-RR_v01r1_blend_s202304190402052_e202304191201136_c202304191229598.nc"
file = f'Samples//{name}'
file = Dataset(file)

# Select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-180.0, -70.00, 0.00, 70.00]
       
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
data = file.variables['RR'][ latli:latui , lonli:lonui ]

# Null values as NaN
data[data == 0] = np.nan

#------------------------------------------------------------------------------------------------------

# Getting the file time and date
date = (name[name.find("_c")+2:name.find(".nc")])
date_file = date
date_formatted = date[0:4] + "-" + date[4:6] + "-" + date[6:8] + " " + date [8:10] + ":" + date [10:12] + " UTC"

# Print the formatted time and date
print("Rain Rate File Date: ", date_formatted)

#------------------------------------------------------------------------------------------------------

# Choose the plot size (width x height, in inches)
plt.figure(figsize=(8,6))

# Use the Mercator projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# Define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# Create a custom color scale:
colors = ["#b9d3f1", "#1751bb", "#80e7cd", "#49bd75", "#3d9942", 
        "#fdf850", "#fed919", "#fb7c07", "#d34800", "#a71d00", 
        "#932349"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
cmap.set_under('#b9d3f1')
cmap.set_over('#932349')
vmin = 0
vmax = 10

# Add some various map elements to the plot to make it recognizable.
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEAN, facecolor='black')

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
plt.colorbar(img, label='Rain Rate (mm/h)', extend='both', orientation='horizontal', pad=0.05, fraction=0.05)

# Add a title
plt.title('Multimission Blended Rain Rate ' + date_formatted, fontweight='bold', fontsize=6, loc='left')
plt.title('Region: ' + str(extent), fontsize=6, loc='right')

#------------------------------------------------------------------------------------------------------

# Show the image
plt.show()