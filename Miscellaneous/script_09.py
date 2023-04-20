#-----------------------------------------------------------------------------------------------------------
# Training - Processing General GNC-A Products With Python - Demonstration: TOAST - GRIB
# Author: Diego Souza (INPE)
#-----------------------------------------------------------------------------------------------------------

# Required modules
import pygrib                               # Provides a high-level interface to the ECWMF ECCODES C library for reading GRIB files
import matplotlib.pyplot as plt             # Plotting library
import cartopy, cartopy.crs as ccrs         # Plot maps
import cartopy.io.shapereader as shpreader  # Import shapefiles
import cartopy.feature as cfeature          # Common drawing and filtering operations
import numpy as np                          # Import the Numpy package
from datetime import datetime, timedelta    # Library to convert julian day to dd-mm-yyyy
import matplotlib.colors                    # Matplotlib colors

#------------------------------------------------------------------------------------------------------

# Open the file using the PyGRIB library
name = "TOAST_Blended-grb_j01_CRIN_j01_OMPS_20230418.grb"
file = f'Samples//{name}'
grib = pygrib.open(file)

# Select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-180.0, -90.0, 180.0, 90.0] 

# Extract the TOAST
toast = grib.select(name='Total column ozone')[0]
toast, lats, lons = toast.data(lat1=extent[1],lat2=extent[3],lon1=extent[0]+360,lon2=extent[2]+360)

#------------------------------------------------------------------------------------------------------

# Getting the file time and date
date = name[name.find("OMPS_")+5:name.find(".grb")]
year = date[0:4]
month = date[4:6]
day = date[6:8]
date_formatted = year + '-' + month + '-' + day

# Print the formatted time and date
print("TOAST File Date: ", date_formatted)

#------------------------------------------------------------------------------------------------------

# To smooth the data
import scipy.ndimage
toast = scipy.ndimage.zoom(toast, 3)
lats = scipy.ndimage.zoom(lats, 3)
lons = scipy.ndimage.zoom(lons, 3)

#------------------------------------------------------------------------------------------------------

# Choose the plot size (width x height, in inches)
plt.figure(figsize=(8,8))

# Use the Mercator projection in cartopy
ax = plt.axes(projection=ccrs.Orthographic(0, 90))

# Define the image extent
img_extent = [extent[0], extent[2], extent[1], extent[3]]

# Create a custom color scale:
cmap = "nipy_spectral"
vmin = 100
vmax = 500

# Plot the image
img = ax.imshow(toast, vmin=vmin, vmax=vmax, origin='upper', extent=img_extent, transform=ccrs.PlateCarree(), cmap=cmap)

# Add a shapefile
shapefile = list(shpreader.Reader('ne_10m_admin_1_states_provinces.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='gray',facecolor='none', linewidth=0.3)

# Add coastlines, borders and gridlines
ax.coastlines(resolution='10m', color='black', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 10), ylocs=np.arange(-90, 90, 10), draw_labels=False)
gl.top_labels = False
gl.right_labels = False

# Add a colorbar
plt.colorbar(img, label='Total ozone (Dobson)', extend='both', orientation='horizontal', pad=0.05, fraction=0.05)

# Add a title
plt.title('Blended TOAST - SNPP OMPS & NOAA-20 CrIS Daily Total Ozone (Northern Hemisphere) ' + date_formatted, fontweight='bold', fontsize=5, loc='left')
plt.title('Region: ' + str(extent), fontsize=5, loc='right')

#------------------------------------------------------------------------------------------------------

# Show the image
plt.show()