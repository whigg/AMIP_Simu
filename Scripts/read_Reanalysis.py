"""
Script reads in monthly data reanalysis (ERA-Interim or ERAi) on grid of 
1.9 x 2.5 (latitude,longitude). Data was interpolated on the model grid using
a bilinear interpolation scheme.
 
Notes
-----
    Author : Zachary Labe
    Date   : 19 February 2019
    
Usage
-----
    [1] readDataR(variable,level,detrend,sliceeq)
    [2] readDataRMeans(variable)
"""

def readDataR(variable,level,detrend,sliceeq):
    """
    Function reads monthly data from ERA-Interim

    Parameters
    ----------
    variable : string
        variable name to read
    level : string
        Height of variable (surface or profile)
    detrend : binary
        True/False whether to remove a linear trend at all grid points
    sliceeq : binary
        True/False whether to slice at the equator for only northern hemisphere
        
        
    Returns
    -------
    lat : 1d numpy array
        latitudes
    lon : 1d numpy array
        longitudes
    time : 1d numpy array
        standard time (months since 1979-1-1, 00:00:00)
    lev : 1d numpy array
        levels (17)
    var : 4d numpy array or 5d numpy array 
        [year,month,lat,lon] or [year,month,level,lat,lon]

    Usage
    -----
    lat,lon,time,lev,var = readDataR(variable,level,detrend)
    """
    print('\n>>> Using readDataR function! \n')
    ###########################################################################
    ###########################################################################
    ###########################################################################
    ### Import modules
    import numpy as np
    from netCDF4 import Dataset
    import calc_Detrend as DT
    
    ### Declare knowns
    months = 12
    years = np.arange(1979,2016+1,1)
    
    if variable == 'SNC':
        years = np.arange(1979,2015+1,1)
    
    ### Directory for experiments (remote server - Seley)
    directorydata = '/seley/zlabe/ERAI/'
    
    ###########################################################################
    ###########################################################################
    ###########################################################################
    ### Read in lat,lon,time from known file 
    if level == 'surface': # 3d variables
        if variable == 'SNC': # Snow data only through 2015!
            dataq = Dataset(directorydata + 'SNC_1979-2016.nc') # 1979-2015
            time = dataq.variables['time'][:]
            lev = 'surface'
            lat = dataq.variables['latitude'][:]
            lon = dataq.variables['longitude'][:]
            dataq.close()
        else:
            dataq = Dataset(directorydata + 'T2M_1979-2016.nc')
            time = dataq.variables['time'][:]
            lev = 'surface'
            lat = dataq.variables['latitude'][:]
            lon = dataq.variables['longitude'][:]
            dataq.close()

    ###########################################################################
    ###########################################################################                 
        if sliceeq == False:
            ### Create empty variable
            varq = np.empty((time.shape[0],lat.shape[0],lon.shape[0]))
            varq[:,:,:] = np.nan ### fill with nans
    
        elif sliceeq == True:
            ### Slice for Northern Hemisphere
            latq = np.where(lat >= 0)[0]
            lat = lat[latq]
            ### Create empty variable
            varq = np.empty((time.shape[0],lat.shape[0],lon.shape[0]))
            varq[:,:,:] = np.nan ### fill with nans
            print('SLICE for Northern Hemisphere!')
        else:
            print(ValueError('Selected wrong slicing!'))
    
    ###########################################################################
    ###########################################################################
    elif level == 'profile': # 4d variables
        dataq = Dataset(directorydata + 'TEMP_1979-2016.nc')
        time = dataq.variables['time'][:]
        lev = dataq.variables['level'][:]
        lat = dataq.variables['latitude'][:]
        lon = dataq.variables['longitude'][:]
        dataq.close()
        
    ###########################################################################
    ###########################################################################
        if sliceeq == False:
            ### Create empty variable
            varq = np.empty((time.shape[0],lev.shape[0],
                             lat.shape[0],lon.shape[0]))
            varq[:,:,:,:] = np.nan ### fill with nans
        elif sliceeq == True:
            ### Slice for Northern Hemisphere
            latq = np.where(lat >= 0)[0]
            lat = lat[latq]
            ### Create empty variable
            varq = np.empty((time.shape[0],lev.shape[0],
                             lat.shape[0],lon.shape[0]))
            varq[:,:,:,:] = np.nan ### fill with nans
            print('SLICE for Northern Hemisphere!')
        else:
            print(ValueError('Selected wrong slicing!'))
    
    ###########################################################################
    ###########################################################################
    else:
        print(ValueError('Selected wrong height - (surface or profile!)!'))
    
    ###########################################################################
    ###########################################################################
    ### Path name for file for each ensemble member
    filename = directorydata + variable + '_1979-2016.nc'
                    
    ###########################################################################
    ###########################################################################
    ### Read in Data
    if sliceeq == False:
        if level == 'surface': # 3d variables
            data = Dataset(filename,'r')
            varq[:,:,:] = data.variables[variable][:]
            print('Completed: Read data %s!' % (variable))   
        elif level == 'profile': # 4d variables
            data = Dataset(filename,'r')
            varq[:,:,:,:] = data.variables[variable][:]
            data.close()
            print('Completed: Read data %s!' % (variable))
        else:
            print(ValueError('Selected wrong height - (surface or profile!)!'))
            
    ###########################################################################
    ###########################################################################
    elif sliceeq == True:
        if level == 'surface': # 3d variables
            data = Dataset(filename,'r')
            varq[:,:,:] = data.variables[variable][:,latq,:]
            data.close()
            print('Completed: Read data %s!' % (variable))      
        elif level == 'profile': # 4d variables
            data = Dataset(filename,'r')
            varq[:,:,:,:] = data.variables[variable][:,:,latq,:]
            data.close()
            print('Completed: Read data %s!' % (variable))
            
        else:
            print(ValueError('Selected wrong height - (surface or profile!)!'))
        
    ###########################################################################
    ###########################################################################
    ###########################################################################
    ### Reshape to split years and months
    if level == 'surface': # 3d variables
        var = np.reshape(varq,(varq.shape[0]//12,months,
                               lat.shape[0],lon.shape[0]))
    elif level == 'profile': # 4d variables
        var = np.reshape(varq,(varq.shape[0]//12,months,lev.shape[0],
                      lat.shape[0],lon.shape[0]))
    else:
        print(ValueError('Selected wrong height - (surface or profile!)!')) 
    print('\nCompleted: Reshaped %s array!' % (variable))
    
    ### Save computer memory
    del varq
    
    ###########################################################################
    ###########################################################################
    ###########################################################################
    ### Convert units
    if variable in ('TEMP','T2M'):
        var = var - 273.15 # Kelvin to degrees Celsius 
        print('Completed: Changed units (K to C)!')
    elif variable == 'SWE':
        var = var*1000. # Meters to Millimeters 
        print('Completed: Changed units (m to mm)!')
    elif variable in ('Z1000','Z850','Z700','Z500','Z300','Z200','Z50','Z30','THICK'):
        var = var/9.80665 # m^2/s^2 divide by gravity m/s^2 to m
        print('Completed: Changed units (m^2/s^2 to m)!')
    elif variable == 'SLP':
        var = var/100. # Pa to hPa
        print('Completed: Changed units (Pa to hPa)!')

    ###########################################################################
    ###########################################################################
    ###########################################################################    
    ### Missing data (fill value to nans)
    var[np.where(var <= -8.99999987e+33)] = np.nan
    var[np.where(var >= 8.99999987e+33)] = np.nan
    print('Completed: Filled missing data to nan!')
    
    ### Detrend data if turned on
    if detrend == True:
        var = DT.detrendDataR(var,level,'monthly')
    
    print('\n>>> Completed: Finished readDataR function!')
    return lat,lon,time,lev,var

###############################################################################
    
def readDataRMeans(variable):
    """
    Function reads monthly data from ERA-Interim. Average
    is taken over the polar cap (65-90, 0-360) and weighted 
    by cosine of latitude. Variables are all 4d.

    Parameters
    ----------
    variable : string
        variable name to read        
        
    Returns
    -------
    lat : 1d numpy array
        latitudes
    lon : 1d numpy array
        longitudes
    lev : 1d numpy array
        levels (17)
    var : 3d numpy array
        [year,month,lev]

    Usage
    -----
    lat,lon,time,lev,var = readDataRMeans(variable)
    """
    print('\n>>> Using readDataRMeans function! \n')
    ###########################################################################
    ###########################################################################
    ###########################################################################
    ### Import modules
    import numpy as np
    from netCDF4 import Dataset
    import calc_Detrend as DT
    
    ### Declare knowns
    months = 12
    years = np.arange(1979,2016+1,1)
    
    ### Directory for experiments (remote server - Seley)
    directorydata = '/seley/zlabe/ERAI/'
    
    ###########################################################################
    ###########################################################################
    dataq = Dataset(directorydata + 'TEMP_1979-2016.nc')
    time = dataq.variables['time'][:]
    lev = dataq.variables['level'][:]
    lat = dataq.variables['latitude'][:]
    lon = dataq.variables['longitude'][:]
    dataq.close()
    
    ###########################################################################
    ###########################################################################                 
    varq = np.empty((time.shape[0],lev.shape[0]))
    varq[:,:] = np.nan ### fill with nans
    
    ###########################################################################
    ###########################################################################
    ### Path name for file for each ensemble member
    filename = directorydata + variable + '_mean_1979-2016.nc'
                    
    ###########################################################################
    ###########################################################################
    ### Read in Data
    data = Dataset(filename,'r')
    varq[:,:] = data.variables[variable][:]
    data.close()
        
    ###########################################################################
    ###########################################################################
    ###########################################################################
    ### Reshape to split years and months
    var = np.reshape(varq,(varq.shape[0]//12,months,lev.shape[0]))
    
    ### Save computer memory
    del varq
    
    ###########################################################################
    ###########################################################################
    ###########################################################################
    ### Convert units
    if variable in ('TEMP','T2M'):
        var = var - 273.15 # Kelvin to degrees Celsius 
        print('Completed: Changed units (K to C)!')
    elif variable == 'SWE':
        var = var*1000. # Meters to Millimeters 
        print('Completed: Changed units (m to mm)!')
    elif variable in ('Z1000','Z850','Z700','Z500','Z300','Z200','Z50','Z30',
                      'GEOP'):
        var = var/9.80665 # m^2/s^2 divide by gravity m/s^2 to m
        print('Completed: Changed units (m^2/s^2 to m)!')
    elif variable == 'SLP':
        var = var/100. # Pa to hPa
        print('Completed: Changed units (Pa to hPa)!')

    ###########################################################################
    ###########################################################################
    ###########################################################################    
    ### Missing data (fill value to nans)
    var[np.where(var <= -8.99999987e+33)] = np.nan
    var[np.where(var >= 8.99999987e+33)] = np.nan
    print('Completed: Filled missing data to nan!')
    
    print('\n>>> Completed: Finished readDataRMeans function!')
    return lat,lon,lev,var
        
#### Test function -- no need to use    
#variable = 'Z500'
#level = 'surface'
#detrend = True
#sliceeq = False
#    
#lat,lon,time,lev,var = readDataR(variable,level,detrend,sliceeq)
#lat,lon,lev,var = readDataRMeans('TEMP')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        