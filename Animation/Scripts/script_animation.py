#-----------------------------------------------------------------------------------------------------------
# Training: Python and GOES-R Imagery: Creating a Professional Plot and Animation, for Any Time Interval
#-----------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------
# REQUIRED MODULES
#-----------------------------------------------------------------------------------------------------------
from netCDF4 import Dataset                                  # Read / Write NetCDF4 files
import matplotlib.pyplot as plt                              # Plotting library
import cartopy, cartopy.crs as ccrs                          # Plot maps
import cartopy.io.shapereader as shpreader                   # Import shapefiles
import numpy as np                                           # Scientific computing with Python
from datetime import datetime, timedelta                     # Basic Dates and time types
import os                                                    # Miscellaneous operating system interfaces
import glob                                                  # Unix style pathname pattern expansion
from shutil import copyfile                                  # Copy files
from osgeo import osr                                        # Python bindings for GDAL
from osgeo import gdal                                       # Python bindings for GDAL
from matplotlib.colors import LinearSegmentedColormap        # Linear interpolation for color maps
from mpl_toolkits.axes_grid1.inset_locator import inset_axes # Add a child inset axes to this existing axes
from utilities import loadCPT                                # Import the CPT convert function
from utilities import download_CMI                           # Our function for download
gdal.PushErrorHandler('CPLQuietErrorHandler')                # Ignore GDAL warnings
#-----------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------
# DOWNLOADING GOES-R NETCDFs 
#-----------------------------------------------------------------------------------------------------------

# Input and output directories
input = "..//Samples"; os.makedirs(input, exist_ok=True)
output = "..//Output"; os.makedirs(output, exist_ok=True)

# Delete all existent files in the 'Output' directory 
files = glob.glob('..//Output//*')
for f in files:
    os.remove(f)
    
# AMAZON repository information 
# https://noaa-goes16.s3.amazonaws.com/index.html
bucket_name = 'noaa-goes16'
product_name = 'ABI-L2-CMIPF'

###################
# USER INPUT: BEGIN
###################

# Desired extent (Min lon, Max lon, Min lat, Max lat)
extent = [-100.0, 0.00, -40.00, 40.00] 

# Desired ABI band
band = '13'

# Start time and date
date_ini = '202007281700'

# End time and date
date_end = '202007291700'

# Interval between images (minutes)
interval = 60

#################
# USER INPUT: END
#################

# Convert the initial and end date to datetime
date_ini = datetime(int(date_ini[0:4]), int(date_ini[4:6]), int(date_ini[6:8]), int(date_ini[8:10]), int(date_ini[10:12]))
date_end = datetime(int(date_end[0:4]), int(date_end[4:6]), int(date_end[6:8]), int(date_end[8:10]), int(date_end[10:12]))

# Create our references for the loop
date_loop = date_ini

#-----------------------------------------------------------------------------------------------------------
# LOOP BETWEEN START AND END DATES - DOWNLOAD, REPROJECTION AND PLOT
#-----------------------------------------------------------------------------------------------------------

# Loop between dates
while (date_loop <= date_end):

    ###############
    # DATA DOWNLOAD
    ###############
    
    # Time / Date for download
    date = date_loop.strftime('%Y%m%d%H%M')
    print('\nDownload time and date:', date)
    
    # Download the GOES-R file
    file_name = download_CMI(date, band, input)
    
    # Read the image
    file = Dataset(f'{input}/{file_name}.nc')

    # Read the band number from the Metadata
    band = str(file.variables['band_id'][0]).zfill(2)
    
    #-----------------------------------------------------------------------------------------------------------
    ########################
    # REPROJECTION WITH GDAL
    ########################
    print("Reprojecting the image")
    
    # Variable
    var = 'CMI'

    # Open the file
    img = gdal.Open(f'NETCDF:{input}/{file_name}.nc:' + var)

    # Read the header metadata
    metadata = img.GetMetadata()
    scale = float(metadata.get(var + '#scale_factor'))
    offset = float(metadata.get(var + '#add_offset'))
    undef = float(metadata.get(var + '#_FillValue'))
    dtime = metadata.get('NC_GLOBAL#time_coverage_start')

    # Load the data
    ds = img.ReadAsArray(0, 0, img.RasterXSize, img.RasterYSize).astype(float)

    # Apply the scale, offset
    ds = (ds * scale + offset) 

    # Read the original file projection and configure the output projection
    source_prj = osr.SpatialReference()
    source_prj.ImportFromProj4(img.GetProjectionRef())

    target_prj = osr.SpatialReference()
    target_prj.ImportFromProj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")

    # Reproject the data
    GeoT = img.GetGeoTransform()
    driver = gdal.GetDriverByName('MEM')
    raw = driver.Create('raw', ds.shape[0], ds.shape[1], 1, gdal.GDT_Float32)
    raw.SetGeoTransform(GeoT)
    raw.GetRasterBand(1).WriteArray(ds)

    # Define the parameters of the output file  
    kwargs = {'format': 'netCDF', \
              'srcSRS': source_prj, \
              'dstSRS': target_prj, \
              'outputBounds': (extent[0], extent[3], extent[2], extent[1]), \
              'outputBoundsSRS': target_prj, \
              'outputType': gdal.GDT_Float32, \
              'srcNodata': undef, \
              'dstNodata': 'nan', \
              'xRes': 0.02, \
              'yRes': 0.02, \
              'resampleAlg': gdal.GRA_NearestNeighbour}

    # Write the reprojected file on disk
    gdal.Warp(f'{output}/{file_name}_rep.nc', raw, **kwargs)
    
    #-----------------------------------------------------------------------------------------------------------
    ###########################
    # OPEN THE REPROJECTED FILE
    ###########################
    
    # Open the reprojected GOES-R image
    file = Dataset(f'{output}/{file_name}_rep.nc')

    # Get the pixel values from the reprojected file
    data = file.variables['Band1'][:]
    #-----------------------------------------------------------------------------------------------------------
    
    ################
    # PLOT THE IMAGE
    ################
    print("Plotting the image")
    
    # Colormap, minimums and maximums, thick interval and legend configuration
    if int(band) <= 6:
        # Converts a CPT file to be used in Python
        cpt = loadCPT('..//Colortables//Square Root Visible Enhancement.cpt')
        cmap = LinearSegmentedColormap('cpt', cpt)
        vmin = 0.0
        vmax = 1.0
        thick_interval = 0.1
        legend_title = 'Reflectance Factor'
    elif int(band) == 7:
        # Converts a CPT file to be used in Python
        cpt = loadCPT('..//Colortables//SVGAIR2_TEMP.cpt')
        cmap = LinearSegmentedColormap('cpt', cpt) 
        data -= 273.15
        vmin = -112.15
        vmax = 56.85
        thick_interval = 10.0
        legend_title = 'Brightness Temperatures (°C)'
    elif int(band) > 7 and int(band) < 11:
        # Converts a CPT file to be used in Python
        cpt = loadCPT('..//Colortables//SVGAWVX_TEMP.cpt')
        cmap = LinearSegmentedColormap('cpt', cpt) 
        data -= 273.15
        vmin = -112.15
        vmax = 56.85
        thick_interval = 10.0
        legend_title = 'Brightness Temperatures (°C)'
    elif int(band) > 10:# and int(band) < 14:
        # Converts a CPT file to be used in Python
        cpt = loadCPT('..//Colortables//IR4AVHRR6.cpt')   
        cmap = LinearSegmentedColormap('cpt', cpt) 
        data -= 273.15    
        vmin = -103.0
        vmax = 84.0
        thick_interval = 10.0
        legend_title = 'Brightness Temperatures (°C)'
    
    #-----------------------------------------------------------------------------------------------------------
        
    ###########################
    # IMAGE SIZE AND PROJECTION
    ###########################
    
    # Choose the plot size (width x height, in inches)
    dpi = 150
    fig = plt.figure(figsize=(data.shape[1]/float(dpi), data.shape[0]/float(dpi)), dpi=dpi)
    
    # Define the projection
    proj = ccrs.PlateCarree()

    # Use the PlateCarree projection in cartopy
    ax = plt.axes([0, 0, 1, 1], projection=proj)
    ax.set_extent([extent[0], extent[2], extent[1], extent[3]], ccrs.PlateCarree())

    # Define the image extent
    img_extent = [extent[0], extent[2], extent[1], extent[3]]
        
    # Plot the image
    img = ax.imshow(data, origin='upper', vmin=vmin, vmax=vmax, extent=img_extent, cmap=cmap)

    ##########################
    # ADD ELEMENTS TO THE PLOT
    ##########################
    
    # To put colorbar inside picture
    axins1 = inset_axes(ax, width="100%", height="1%", loc='lower center', borderpad=0.0)

    # Add a shapefile
    shapefile = list(shpreader.Reader('..//Shapefiles//ne_10m_admin_1_states_provinces.shp').geometries())
    ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='white',facecolor='none', linewidth=0.5)

    # Add coastlines, borders and gridlines
    ax.coastlines(resolution='10m', color='cyan', linewidth=2.0)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='turquoise', linewidth=1.0)
    gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=0.5, linestyle='--', linewidth=1.0, xlocs=np.arange(-180, 180, 5), ylocs=np.arange(-90, 90, 5), draw_labels=True)
    gl.bottom_labels = False
    gl.right_labels = False
    gl.xpadding = -5
    gl.ypadding = -15

    # Extract the time / date from the NetCDF
    date = (datetime.strptime(dtime, '%Y-%m-%dT%H:%M:%S.%fZ'))

    # Add a title
    date = date.strftime('%Y-%m-%d %H:%M')
    plt.annotate(f'GEONETCast-Americas Training for Eastern Caribbean States - GOES-16 Band {band} {date} UTC', xy=(0.01, 0.97), xycoords='figure fraction', fontsize=15, fontweight='bold', color='white', bbox=dict(boxstyle="round",fc=(0.0, 0.0, 0.0), ec=(1., 1., 1.)))

    # Add logos / images to the plot
    my_logo = plt.imread('..//Logos//my_logo.png')
    newax = fig.add_axes([0.01, 0.03, 0.10, 0.10], anchor='SW') #  [left, bottom, width, height]. All quantities are in fractions of figure width and height.
    newax.imshow(my_logo)
    newax.axis('off')
    
    # Add a colorbar inside the plot
    ticks = np.arange(vmin, vmax, thick_interval).tolist()     
    ticks =  thick_interval * np.round(np.true_divide(ticks,thick_interval))
    ticks = ticks[1:]
    cb = fig.colorbar(img, cax=axins1, orientation="horizontal", ticks=ticks)
    cb.set_label(label=legend_title, color='black', size=10, weight='bold')
    cb.outline.set_visible(False)
    cb.ax.tick_params(width = 0)
    cb.ax.xaxis.set_tick_params(pad=-int(data.shape[0] * 0))
    cb.ax.xaxis.set_ticks_position('top')
    cb.ax.xaxis.set_label_position('top')
    cb.ax.tick_params(axis='x', colors='black', labelsize=int(data.shape[0] * 0.005))

    ################
    # ADD A SCALEBAR
    ################
    
    # Add a scalebar
    from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
    import matplotlib.font_manager as fm
    fontprops = fm.FontProperties(size=10)
    distance = 1000
    scalebar = AnchoredSizeBar(ax.transData,
                              (distance / 111),
                              str(distance) + ' km',
                              loc='lower right',
                              pad=0.1,
                              borderpad=2.5,
                              color='black',
                              frameon=True,
                              label_top=True,
                              sep=5,
                              size_vertical=0.5,
                              fontproperties=fontprops
                              )
    ax.add_artist(scalebar)
    
    # Plot the N arrow
    import matplotlib.patheffects as patheffects
    buffer = [patheffects.withStroke(linewidth=5, foreground="w")]
    t1 = ax.text(0.91, 0.070, u'\u25B2\nN', transform=ax.transAxes,
    horizontalalignment='center', verticalalignment='bottom',
    path_effects=buffer)

    ################
    # ADD LABELS
    ################
    
    # Add a circle
    ax.plot(-61.7927, 17.1402, 'o', color='red', markersize=5, transform=ccrs.Geodetic(), markeredgewidth=1.0, markeredgecolor=(0, 0, 0, 1))
    # Add a text
    txt = ax.text(-61.7927 + 0.4, 17.1402 + 0.1, "Antigua and Barbuda", fontsize='12', fontweight='bold', color='gold', transform=ccrs.Geodetic())
    # Style the text
    txt.set_path_effects([patheffects.withStroke(linewidth=2, foreground='black')])

    # Add a circle
    ax.plot(-59.4870, 13.0858, 'o', color='red', markersize=5, transform=ccrs.Geodetic(), markeredgewidth=1.0, markeredgecolor=(0, 0, 0, 1))
    # Add a text
    txt = ax.text(-59.4870 + 0.4, 13.0858 + 0.0, "Barbados", fontsize='12', fontweight='bold', color='gold', transform=ccrs.Geodetic())
    # Style the text
    txt.set_path_effects([patheffects.withStroke(linewidth=2, foreground='black')])
    
    # Add a circle
    ax.plot(-61.3916, 15.3388, 'o', color='red', markersize=5, transform=ccrs.Geodetic(), markeredgewidth=1.0, markeredgecolor=(0, 0, 0, 1))
    # Add a text
    txt = ax.text(-61.3916 + 0.4, 15.3388 + 0.4, "Dominica", fontsize='12', fontweight='bold', color='gold', transform=ccrs.Geodetic())
    # Style the text
    txt.set_path_effects([patheffects.withStroke(linewidth=2, foreground='black')])

    # Add a circle
    ax.plot(-61.7433, 12.0469, 'o', color='red', markersize=5, transform=ccrs.Geodetic(), markeredgewidth=1.0, markeredgecolor=(0, 0, 0, 1))
    # Add a text
    txt = ax.text(-61.7433 + 0.4, 12.0469 + 0.4, "Grenada", fontsize='12', fontweight='bold', color='gold', transform=ccrs.Geodetic())
    # Style the text
    txt.set_path_effects([patheffects.withStroke(linewidth=2, foreground='black')])
    
    # Add a circle
    ax.plot(-62.7079, 17.2889, 'o', color='red', markersize=5, transform=ccrs.Geodetic(), markeredgewidth=1.0, markeredgecolor=(0, 0, 0, 1))
    # Add a text
    txt = ax.text(-62.7079 + 0.4, 17.2889 + 0.4, "St Kitts & Nevis", fontsize='12', fontweight='bold', color='gold', transform=ccrs.Geodetic())
    # Style the text
    txt.set_path_effects([patheffects.withStroke(linewidth=2, foreground='black')])
    
    # Add a circle
    ax.plot(-61.1517, 13.1579, 'o', color='red', markersize=5, transform=ccrs.Geodetic(), markeredgewidth=1.0, markeredgecolor=(0, 0, 0, 1))
    # Add a text
    txt = ax.text(-61.1517 + 0.4, 13.1579 + 0.4, "St Vincent & Grenadines", fontsize='12', fontweight='bold', color='gold', transform=ccrs.Geodetic())
    # Style the text
    txt.set_path_effects([patheffects.withStroke(linewidth=2, foreground='black')])
    
    # Add a circle
    ax.plot(-60.9503, 13.7364, 'o', color='red', markersize=5, transform=ccrs.Geodetic(), markeredgewidth=1.0, markeredgecolor=(0, 0, 0, 1))
    # Add a text
    txt = ax.text(-60.9503 + 0.4, 13.7364 + 0.4, "St Lucia", fontsize='12', fontweight='bold', color='gold', transform=ccrs.Geodetic())
    # Style the text
    txt.set_path_effects([patheffects.withStroke(linewidth=2, foreground='black')])
    
    #-----------------------------------------------------------------------------------------------------------
    
    ###########################################
    # SAVE THE IMAGE AND DELETE AUXILIARY FILES
    ###########################################
    
    # Save the image
    plt.savefig(f'{output}/{file_name}_rep.png', bbox_inches='tight', pad_inches=0, dpi=300)
    
    # Delete the original and the reprojected NetCDF files
    import os
    file.close()
    os.remove(f'{output}/{file_name}_rep.nc')
    os.remove(f'{input}/{file_name}.nc')
       
    ######################
    # UPDATE THE ANIMATION
    ######################
    
    print("Updating the animation")
    
    # Create a list that will store the files
    files = []
    
    # Directory with the images
    directory = "..//Output//"
    
    # Directory with the HMTL structure 
    outdir = "..//HTML//"
    
    # File identifier (unique string inside the file name)
    identifier = 'OR_ABI-L2-CMIPF-*.png'
    
    # Rename string (the final file name for the animation will be this + a number
    rename_id = 'img_'
    
    # Add to the list the files in the dir that matches the identifier
    for filename in sorted(glob.glob(directory + identifier)):
        files.append(filename)
    
    # Maximum number of animation frames 
    max_files = 24  
    
    # Keep on the list only the max number of files
    files = files[-max_files:]
    
    # Copy the files to the HTML Output folder, following the HTML naming convention
    for idx, val in enumerate(files):
        src = val
        dst = outdir + rename_id + str(idx + 1) + '.png'
        copyfile(src, dst)    
    
    # Get the number of files on the folder
    num_files = len(files)
    
    # Get the difference of desired files and available files
    diff_files = max_files - num_files
    
    # If there are less files than the maximum HTML animation files, repeat the last one "x" times
    if diff_files > 0:
        for i in range(diff_files):
            dst = outdir + rename_id + str(num_files + i + 1) + '.png'       
            copyfile(files[-1], dst)
    
    # Close the image
    plt.close()
        
    # Increment the date_ini
    date_loop = date_loop + timedelta(minutes=interval)