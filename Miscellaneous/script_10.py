#-----------------------------------------------------------------------------------------------------------
# Training - Processing General GNC-A Products With Python - Demonstration: Fire / Hotspots Shapefile
# Author: Diego Souza (INPE)
#-----------------------------------------------------------------------------------------------------------

# Required modules
import matplotlib.pyplot as plt             # Plotting library
import cartopy, cartopy.crs as ccrs         # Plot maps
import cartopy.io.shapereader as shpreader  # Import shapefiles
import cartopy.feature as cfeature          # Common drawing and filtering operations
import numpy as np                          # Import the Numpy package
from datetime import datetime, timedelta    # Library to convert julian day to dd-mm-yyyy
import matplotlib.colors                    # Matplotlib colors

#------------------------------------------------------------------------------------------------------

# Choose the plot size (width x height, in inches)
plt.figure(figsize=(7,5))

# Use the Plate Carree projection in cartopy
ax = plt.axes(projection=ccrs.PlateCarree())

# Select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-90.0, 10.00, -55.00, 30.00]
ax.set_extent([extent[0], extent[2], extent[1], extent[3]])

# Add some various map elements to the plot to make it recognizable.
ax.add_feature(cfeature.LAND)
#ax.add_feature(cfeature.OCEAN)
ax.add_feature(cfeature.OCEAN, facecolor='dimgrey')

# Add a shapefile
shapefile = list(shpreader.Reader('ne_10m_admin_1_states_provinces.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='gray',facecolor='none', linewidth=0.3)

# Add coastlines, borders and gridlines
ax.coastlines(resolution='10m', color='black', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 10), ylocs=np.arange(-90, 90, 10), draw_labels=True)
gl.top_labels = False
gl.right_labels = False

# Reading the fire hotspots
name = "INPE_MVF_202304190000.shp"
file = f'Samples//{name}'
points = list(cartopy.io.shapereader.Reader(file).geometries())
ax.scatter([point.x for point in points],
           [point.y for point in points],
           transform=ccrs.Geodetic(), s=10, color='red')

# Getting the file time and date
date = (name[name.find("MVF_")+4:name.find(".shp")])
date_formatted = date[0:4] + '-' + date[4:6] + '-' + date[6:8] 

# Print the formatted time and date
print("Fire / Hotspots File Date: ", date_formatted)

# Add a title
plt.title('Multimission - Fire / Hotspots ' + date_formatted, fontweight='bold', fontsize=7, loc='left')
plt.title('Region: ' + str(extent), fontsize=7, loc='right')

#------------------------------------------------------------------------------------------------------

# Show the image
plt.show()