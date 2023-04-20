#-----------------------------------------------------------------------------------------------------------
# Training - Processing General GNC-A Products With Python - Demonstration: CIRA ALPW HDF's
# Author: Diego Souza (INPE)
#-----------------------------------------------------------------------------------------------------------

# Required modules
from pyhdf.SD import SD, SDC                # Import the PyHDF library
import matplotlib.pyplot as plt             # Plotting library
import cartopy, cartopy.crs as ccrs         # Plot maps
import cartopy.io.shapereader as shpreader  # Import shapefiles
import numpy as np                          # Import the Numpy package
from datetime import datetime, timedelta    # Library to convert julian day to dd-mm-yyy
import matplotlib.colors                    # Matplotlib colors

#------------------------------------------------------------------------------------------------------

# Reading the ALPW HDF file
name = "2021188120000_ADVECT_COMPOSITE.HDF"
file = f'Samples//{name}'
hdf = SD(file, SDC.READ)

# Reading the desiref dataset
# Available options: ['ALPW_1000_0850_hPa_Mean', 'ALPW_0850_0700_hPa_Mean', 'ALPW_0700_0500_hPa_Mean', 'ALPW_0500_0300_hPa_Mean']
sds_obj = hdf.select('ALPW_1000_0850_hPa_Mean') 
data = sds_obj.get() 

#------------------------------------------------------------------------------------------------------

# Select the extent [min. lon, min. lat, max. lon, max. lat]
extent = [-100.0, 0.00, -40.00, 40.00]

# Reading the latitudes and longitudes from the reference files (provided by the ALPW developer)
lats = np.loadtxt('alpw_lats.txt')
lons = np.loadtxt('alpw_lons.txt')

# Latitude lower and upper index:
latli = np.argmin( np.abs( lats - extent[1] ) )
latui = np.argmin( np.abs( lats - extent[3] ) )
 
# Longitude lower and upper index: 
if (extent[2] > 20):
  lonli = np.argmin( np.abs( lons - extent[0] ) )
  lonui = np.argmin( np.abs( extent[2] - lons ) )
  data1 = data[latui:latli , lonli:2499]
  data2 = data[latui:latli , 0:lonui]
  data = np.hstack((data1, data2))
else:
  lonli = np.argmin( np.abs( lons - extent[0] ) )
  lonui = np.argmin( np.abs( lons - extent[2] ) )
  data = data[latui:latli , lonli:lonui]

#------------------------------------------------------------------------------------------------------

# Converting the extents from epsg:4326 to epsg:3857
import pyproj

proj = pyproj.Transformer.from_crs(4326, 3857, always_xy=True)
x1,y1 = (extent[0], extent[1])
x2,y2 = (extent[2], extent[3])
a, b = proj.transform(x1, y1)
c, d = proj.transform(x2, y2)
extent_mercator = [a,b,c,d]

print("Extent converted to Mercator (m): ", extent_mercator)

#------------------------------------------------------------------------------------------------------

# Reading the time and date from the file name
date = name[0:13]
year = date[0:4]; jday = date[4:7]; hour = date[7:9]; minute = date[9:11]; seconds = date[11:13]

# Formatting the date
date_formatted = (datetime.strptime(year + jday, '%Y%j').date().strftime('%Y-%m-%d')) + ' ' +  hour + ':' + minute + ':' + seconds + ' UTC'

# Print the formatted time and date
print("ALPW File Date: ", date_formatted)

#------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------

# Choose the plot size (width x height, in inches)
plt.figure(figsize=(8,7))

# Use the Mercator projection in cartopy
ax = plt.axes(projection=ccrs.Mercator())

# Define the image extent
img_extent = [extent_mercator[0], extent_mercator[2], extent_mercator[1], extent_mercator[3]]

# Create a custom color scale based in the ALPW web page (http://cat.cira.colostate.edu/sport/layered/advected/LPW_SAm.htm)
colors = ["#000000", "#393939", "#818181", "#bec4ba", "#339831", "#056c47", 
          "#1360a7", "#1b91fc", "#0ca7f0", "#00d6ef", "#5c92d8", "#8954d1", 
          "#922fed", "#8b07a0", "#8d0069", "#8c0002", "#cc0000", "#e22a00", 
          "#f56200", "#d25d00", "#9b3900", "#dc9e00", "#ffe300", "#fffa08", 
          "#dd928c", "#e5a3a6"]
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", colors)
vmin = 0
vmax = 32
    
# Plot the image
img = ax.imshow(data, vmin=vmin, vmax=vmax, origin='upper', extent=img_extent, cmap=cmap)

# Add a shapefile
shapefile = list(shpreader.Reader('ne_10m_admin_1_states_provinces.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='white',facecolor='none', linewidth=0.3)

# Add coastlines, borders and gridlines
ax.coastlines(resolution='10m', color='white', linewidth=0.8)
ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 10), ylocs=np.arange(-90, 90, 10), draw_labels=True)
gl.top_labels = False
gl.right_labels = False

# Add a colorbar
plt.colorbar(img, label='Advected Layered Precipitable Water (mm)', extend='both', orientation='horizontal', pad=0.04, fraction=0.05)

# Add a title
plt.title('CIRA ALPW 16 km ' + date_formatted, fontweight='bold', fontsize=13, loc='left')
plt.title('Sfc - 850 mb', fontsize=13, loc='right')

#------------------------------------------------------------------------------------------------------

# Show the image
plt.show()