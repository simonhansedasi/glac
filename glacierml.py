# import sys
# !{sys.executable} -m pip install 
import tensorflow as tf
import pandas as pd
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers.experimental import preprocessing
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
import geopy.distance
pd.set_option('mode.chained_assignment',None)

'''
RGI_loader


'''
def RGI_loader(pth = '/data/fast1/glacierml/T_models/RGI/rgi60-attribs/'):
    RGI_extra = pd.DataFrame()
    for file in tqdm(os.listdir(pth)):
        file_reader = pd.read_csv(pth+file, encoding_errors = 'replace', on_bad_lines = 'skip')
        RGI_extra = RGI_extra.append(file_reader)
    RGI = RGI_extra[[
        'CenLat',
        'CenLon',
        'Slope',
        'Zmin',
        'Zmed',
        'Zmax',
        'Area',
        'Aspect',
        'Lmax'
    ]]
    return RGI


'''
data_loader
input = path to GlaThiDa data. Default coded in.
output = dataframe containing glacier-scale GlaThiDa information with null entries dropped.
'''
def data_loader_01(pth_1 = '/data/fast1/glacierml/T_models/T_data/'):
    print('Importing glacier data')
    glacier = pd.read_csv(pth_1 + 'glacier.csv', low_memory = False)
    df = glacier[[
        'id',
        'lat',
        'lon',
        'area',
        'mean_slope',
        'mean_thickness'
    ]]
        
    df = df.dropna()
    df = df.drop('id',axis = 1)
    return df

def data_loader_02(pth_1 = '/data/fast1/glacierml/T_models/T_data/'):
    print('Importing glacier data')
    T = pd.read_csv(pth_1 + 'T.csv', low_memory = False)
    df = T[[
#         'id',
        'LAT',
        'LON',
        'AREA',
        'MEAN_SLOPE',
        'MEAN_THICKNESS'
    ]]
        
    df = df.dropna(subset = ['MEAN_SLOPE'])
    df = df.dropna(subset = ['MEAN_THICKNESS'])
#     df = df.drop('id',axis = 1)
    return df




def data_loader_031(
    pth_1 = '/data/fast1/glacierml/T_models/T_data/',
    pth_2 = '/data/fast1/glacierml/T_models/RGI/rgi60-attribs/',
    pth_3 = '/data/fast1/glacierml/T_models/matched_indexes/'
):
    print('matching GlaThiDa and RGI data method 4...')
    RGI = pd.DataFrame()
    for file in os.listdir(pth_2):
        file_reader = pd.read_csv(pth_2 + file, encoding_errors = 'replace', on_bad_lines = 'skip')
        RGI = RGI.append(file_reader, ignore_index = True)

    glathida = pd.read_csv(pth_1 + 'glacier.csv')
    indexes = pd.read_csv(pth_3 + 'GlaThiDa_RGI_matched_indexes_4.csv')
    indexes = indexes.rename(columns = {
        'name':'name_g',
        'Name':'name_r',
        'area':'area_g',
        'Area':'area_r',
        'BgnDate':'date_r',
        'date':'date_g'


    })
    df = indexes[[
        'CenLat',
        'CenLon',
    #     'LAT',
    #     'LON',
        'Lmax',
#         'Zmin',
        'Zmed',
#         'Zmax',
        'mean_thickness',
    #     'GlaThiDa_index',
    #     'RGI_index',
        'area_g',
        'area_r',
#         'Aspect',
        'Slope',
    #     'name_r',
    #     'name_g',
    #     'date_r',
    #     'date_g'
    ]]

    df['size_anomaly'] = abs(df['area_g'] - df['area_r'])
    df = df[df['size_anomaly'] < 1]
    df = df.drop([
        'size_anomaly',
        'area_g'
#         'area_r'
    ], axis = 1)
    
    df = df.rename(columns = {
        'area_r':'Area'
    })
    
    df = df.drop(df.loc[df['Zmed']<0].index)
    df = df.drop(df.loc[df['Lmax']<0].index)
    df = df.drop(df.loc[df['Slope']<0].index)
#     df = df.drop(df.loc[df['Aspect']<0].index)
    df = df.reset_index()
    df = df.drop('index', axis=1)
    
    
    
    
    
    return df

'''


'''
def GlaThiDa_RGI_index_matcher_1(
    pth_1 = '/data/fast1/glacierml/T_models/T_data/',
    pth_2 = '/data/fast1/glacierml/T_models/RGI/rgi60-attribs/',
    pth_3 = '/data/fast1/glacierml/T_models/matched_indexes/'
):    
    T = pd.read_csv(pth_1 + 'T.csv', low_memory = False)
    T = T.dropna(subset = ['MEAN_THICKNESS'])

    RGI_extra = pd.DataFrame()
    for file in os.listdir(pth_2):
        print(file)
        file_reader = pd.read_csv(pth_2 + file, encoding_errors = 'replace', on_bad_lines = 'skip')
        RGI_extra = RGI_extra.append(file_reader, ignore_index = True)

    RGI_coordinates = RGI_extra[[
        'CenLat',
        'CenLon'
    ]]
    RGI_coordinates

    df = pd.DataFrame(columns = ['GlaThiDa_index','RGI_index'])
    for T_idx in tqdm(T.index):
        GlaThiDa_coords = (T['LAT'].loc[T_idx],
                           T['LON'].loc[T_idx])
    #     print(GlaThiDa_coords)
        for RGI_idx in RGI_coordinates.index:
    #         print(RGI_idx)
            RGI_coords = (RGI_coordinates['CenLat'].loc[RGI_idx],
                          RGI_coordinates['CenLon'].loc[RGI_idx])
            distance = geopy.distance.geodesic(GlaThiDa_coords, RGI_coords).km
            if distance < 1:
#                 print('DING!')
#                 print(T_idx)
#                 print(RGI_idx)
#                 print(RGI_coords)
                f = pd.Series(distance, name='distance')
                df = df.append(f, ignore_index=True)
                df['GlaThiDa_index'].iloc[-1] = T_idx
                df['RGI_index'].iloc[-1] = RGI_idx
                    
                df.to_csv(pth_3 + 'GlaThiDa_RGI_matched_indexes_1_live.csv')

                break
'''
data_loader_1
input = path to GlaThiDa data. Default coded in.
output = dataframe containing glacier-scale GlaThiDa information with null entries dropped paired with RGI attributes.
'''
def data_loader_1(
    pth_1 = '/data/fast1/glacierml/T_models/T_data/',
    pth_2 = '/data/fast1/glacierml/T_models/RGI/rgi60-attribs/',
    pth_3 = '/data/fast1/glacierml/T_models/matched_indexes/'
):
    print('matching GlaThiDa and RGI data method 1...')
    # load GlaThiDa T.csv -- older version than glacier.csv
    T = pd.read_csv(pth_1 + 'T.csv', low_memory = False)
    
    # RGI is separated by region. This loop reads each one in order and appends it to a df
    RGI_extra = pd.DataFrame()
    for file in os.listdir(pth_2):
        file_reader = pd.read_csv(pth_2 + file, encoding_errors = 'replace', on_bad_lines = 'skip')
        RGI_extra = RGI_extra.append(file_reader, ignore_index = True)
    
    
    # read csv of combined indexes
    comb = pd.read_csv(pth_3 + 'GlaThiDa_RGI_matched_indexes_1.csv')
#     drops = comb.index[comb['0']!=0]
#     comb = comb.drop(drops)
    comb = comb.drop_duplicates(subset = 'RGI_index', keep = 'last')
    
    # isloate T and RGI data to only what GlaThiDa indexes are matched 
    T = T.loc[comb['GlaThiDa_index']]
    RGI = RGI_extra.loc[comb['RGI_index']]
    
    # reset indexes for clean df, will crash otherwise.
    # RGI and T data are lined up, indexes are not needed
    RGI = RGI.reset_index()
    T = T.reset_index()
    
    # merge and select data
    df1 = pd.merge(T, RGI, left_index=True, right_index=True)


    df1 = df1[[
#         'LAT',
#         'LON',
#         'AREA',
        'CenLon',
        'CenLat',
        'Area',
        'MEAN_THICKNESS',
        'Slope',
        'Zmin',
        'Zmed',
        'Zmax',
        'Aspect',
        'Lmax'
    ]]
    df1 = df1.dropna(subset = ['MEAN_THICKNESS'])
    
    return df1


'''

'''    
def GlaThiDa_RGI_index_matcher_2(
    pth_1 = '/data/fast1/glacierml/T_models/T_data/',
    pth_2 = '/data/fast1/glacierml/T_models/RGI/rgi60-attribs/',
    pth_3 = '/data/fast1/glacierml/T_models/matched_indexes/'
):
    T = pd.read_csv(pth_1 + 'glacier.csv', low_memory = False)
    T = T.dropna(subset = ['mean_thickness'])

    RGI_extra = pd.DataFrame()
    for file in os.listdir(pth_2):
        print(file)
        file_reader = pd.read_csv(pth_2 + file, encoding_errors = 'replace', on_bad_lines = 'skip')
        RGI_extra = RGI_extra.append(file_reader, ignore_index = True)

    RGI_coordinates = RGI_extra[[
        'CenLat',
        'CenLon'
    ]]

    df = pd.DataFrame(columns = ['GlaThiDa_index', 'RGI_index'])
    for T_idx in tqdm(T.index):
        GlaThiDa_coords = (T['lat'].loc[T_idx],
                           T['lon'].loc[T_idx])
    #     print(GlaThiDa_coords)
        for RGI_idx in RGI_coordinates.index:
    #         print(RGI_idx)
            RGI_coords = (RGI_coordinates['CenLat'].loc[RGI_idx],
                          RGI_coordinates['CenLon'].loc[RGI_idx])

            distance = geopy.distance.geodesic(GlaThiDa_coords,RGI_coords).km
            if 0 <= distance < 1:
    #             print(RGI_coords)
                f = pd.Series(distance, name='distance')
                df = df.append(f, ignore_index=True)
                df['GlaThiDa_index'].iloc[-1] = T_idx
                df['RGI_index'].iloc[-1] = RGI_idx
                df.to_csv(pth_3 + 'GlaThiDa_RGI_matched_indexes_2_live.csv')


'''
data_loader_2
input = path to GlaThiDa data. Default coded in.
output = dataframe containing glacier-scale GlaThiDa information with null entries dropped paired with RGI attributes. GlaThiDa and RGI are matched using a different, more rigorous technique than data_loader_2()
'''
def data_loader_2(
    pth_1 = '/data/fast1/glacierml/T_models/T_data/',
    pth_2 = '/data/fast1/glacierml/T_models/RGI/rgi60-attribs/',
    pth_3 = '/data/fast1/glacierml/T_models/matched_indexes/'
):
    print('matching GlaThiDa and RGI data method 2...')
    
    # read csv of combined indexes and GlaThiDa glacier.csv data
    comb = pd.read_csv(pth_3 + 'GlaThiDa_RGI_matched_indexes_2.csv')
    comb = comb.rename(columns = {'0':'distance'})

    glacier = pd.read_csv(pth_1 + 'glacier.csv')
    glacier = glacier.dropna(subset = ['mean_thickness'])

    comb = comb[[
        'GlaThiDa_index',
        'RGI_index',
        'distance'
    ]]
    
    # create combined indexes, a df cleaned to have only one selection of GlaThiDa and RGI
    combined_indexes = pd.DataFrame()    
    
    # This loop goes through comb and picks glaciers with minimum distance between RGI and GlaTHiDa
    for GlaThiDa_index in comb['GlaThiDa_index'].index:
        df = comb[comb['GlaThiDa_index'] == GlaThiDa_index]
        f = df.loc[df[df['distance'] == df['distance'].min()].index]
        combined_indexes = combined_indexes.append(f)
    # drop any duplicates that may have had equal distance to RGI
    combined_indexes = combined_indexes.drop_duplicates(subset = ['GlaThiDa_index'])
    combined_indexes = combined_indexes.reset_index()
    combined_indexes = combined_indexes[[
        'GlaThiDa_index',
        'RGI_index',
        'distance'
    ]]
    
    # build RGI
    RGI_extra = pd.DataFrame()
    
    
    # RGI is separated by region. This loop reads each one in order and appends it to a df
    for file in os.listdir(pth_2):
        file_reader = pd.read_csv(pth_2 + file, encoding_errors = 'replace', on_bad_lines = 'skip')
        RGI_extra = RGI_extra.append(file_reader, ignore_index = True)
    
    # data is a df to combine GlaThiDa thicknesses with RGI attributes
    data = pd.DataFrame(columns = ['GlaThiDa_index', 'thickness'])
    
    # iterate over each GlaThiDa index in combined_indexes, the df combining GlaThiDa and RGI indexes
    for GlaThiDa in combined_indexes['GlaThiDa_index'].index:
        
        # find GlaThiDa thickness from glacier df using GlaThiDa index from combined indexes
        glathida_thickness = glacier['mean_thickness'].iloc[GlaThiDa] 
        
        # find what RGI is lined up with that GlaThiDa glacier
        rgi_index = combined_indexes['RGI_index'].loc[GlaThiDa]
        
        # locate RGI data from RGI_extra via RGI index matched with GlaThiDa index
        rgi = RGI_extra.iloc[[rgi_index]]
        
        # append RGI attributes to GlaThiDa index and thickness
        data = data.append(rgi)
        
        # locate most recently appended row to df and populate GlaThiDa_index and thickness
        data['GlaThiDa_index'].iloc[-1] = combined_indexes['GlaThiDa_index'].loc[GlaThiDa]
        data['thickness'].iloc[-1] = glathida_thickness
    
    # drop any extra RGI that may have made their way in and reset index
    data = data.drop_duplicates(subset = ['RGIId'])
    data = data.reset_index()
    
    # load what data we need for training
    df2 = data[[
    #     'RGIId',
#         'GlaThiDa_index',
        'CenLon',
        'CenLat',
        'Area',
        'thickness',
        'Zmin',
        'Zmed',
        'Zmax',
        'Slope',
        'Aspect',
        'Lmax'
    ]]
    # for some reason thickness was an object after selected from df. Here we make it a number
    df2['thickness'] = pd.to_numeric(df2['thickness'])
    
    return df2


'''

'''
def GlaThiDa_RGI_index_matcher_3(
    pth_1 = '/data/fast1/glacierml/T_models/T_data/',
    pth_2 = '/data/fast1/glacierml/T_models/RGI/rgi60-attribs/',
    pth_3 = '/data/fast1/glacierml/T_models/matched_indexes/'
):
    glathida = pd.read_csv(pth_1 + 'T.csv')
    glathida = glathida.dropna(subset = ['MEAN_THICKNESS'])

    RGI = pd.DataFrame()
    for file in os.listdir(pth_2):
        print(file)
        file_reader = pd.read_csv(pth_2 + file, encoding_errors = 'replace', on_bad_lines = 'skip')
        RGI = RGI.append(file_reader, ignore_index = True)

    df = pd.DataFrame(columns = ['GlaThiDa_index', 'RGI_index'])
    #iterate over each glathida index
    for i in tqdm(glathida.index):
        #obtain lat and lon from glathida 
        glathida_ll = (glathida.loc[i].LAT,glathida.loc[i].LON)
        
        # find distance between selected glathida glacier and all RGI
        distances = RGI.apply(
            lambda row: geopy.distance.geodesic((row.CenLat,row.CenLon),glathida_ll),
            axis = 1
        )
        
        # find index of minimum distance between glathida and RGI glacier
        RGI_index = np.argmin(distances)
        RGI_match = RGI.loc[RGI_index]
        
        # concatonate two rows and append to dataframe with indexes for both glathida and RGI
        temp_df = pd.concat([RGI_match, glathida.loc[i]], axis = 0)
        df = df.append(temp_df, ignore_index = True)
    #     df = df.append(GlaThiDa_and_RGI, ignore_index = True)
        df['GlaThiDa_index'].iloc[-1] = i
        df['RGI_index'].iloc[-1] = RGI_index
        
    df['GlaThiDa_index'] = df['GlaThiDa_index'].astype(int)
    df['RGI_index'] = df['RGI_index'].astype(int)
    df.to_csv(pth_3 + 'GlaThiDa_RGI_matched_indexes_3_live.csv')
    
    
'''

'''
def data_loader_3(
    pth_1 = '/data/fast1/glacierml/T_models/T_data/',
    pth_2 = '/data/fast1/glacierml/T_models/RGI/rgi60-attribs/',
    pth_3 = '/data/fast1/glacierml/T_models/matched_indexes/'
):
    print('matching GlaThiDa and RGI data method 3...')
    RGI = pd.DataFrame()
    for file in os.listdir(pth_2):
        file_reader = pd.read_csv(pth_2 + file, encoding_errors = 'replace', on_bad_lines = 'skip')
        RGI = RGI.append(file_reader, ignore_index = True)

    glathida = pd.read_csv(pth_1 + 'T.csv')
    indexes = pd.read_csv(pth_3 + 'GlaThiDa_RGI_matched_indexes_3.csv')
#     indexes = indexes.rename(columns = {
#         'GLACIER_NAME':'name_g',
#         'Name':'name_r',
#         'AREA':'area_g',
#         'Area':'area_r',
#         'BgnDate':'date_r',
#         'SURVEY_DATE':'date_g'


#     })
    df = indexes[[
        'CenLat',
        'CenLon',
    #     'LAT',
    #     'LON',
        'Area',
        'Lmax',
        'Zmin',
        'Zmed',
        'Zmax',
        'MEAN_THICKNESS',
    #     'GlaThiDa_index',
    #     'RGI_index',
#         'area_g',
#         'area_r',
        'Aspect',
        'Slope',
    #     'name_r',
    #     'name_g',
    #     'date_r',
    #     'date_g'
    ]]

#     df['size_anomaly'] = abs(df['area_g'] - df['area_r'])
#     df = df[df['size_anomaly'] < 1]
#     df = df.drop([
#         'size_anomaly',
#         'area_g'
# #         'area_r'
#     ], axis = 1)
    
#     df = df.rename(columns = {
#         'area_r':'Area'
#     })
    return df
    
    
    
'''

'''
def GlaThiDa_RGI_index_matcher_4(
    pth_1 = '/data/fast1/glacierml/T_models/T_data/',
    pth_2 = '/data/fast1/glacierml/T_models/RGI/rgi60-attribs/',
    pth_3 = '/data/fast1/glacierml/T_models/matched_indexes/'
):
    glathida = pd.read_csv(pth_1 + 'glacier.csv')
    glathida = glathida.dropna(subset = ['mean_thickness'])

    RGI = pd.DataFrame()
    for file in os.listdir(pth_2):
        print(file)
        file_reader = pd.read_csv(pth_2 + file, encoding_errors = 'replace', on_bad_lines = 'skip')
        RGI = RGI.append(file_reader, ignore_index = True)

    df = pd.DataFrame(columns = ['GlaThiDa_index', 'RGI_index'])
    #iterate over each glathida index
    for i in tqdm(glathida.index):
        #obtain lat and lon from glathida 
        glathida_ll = (glathida.loc[i].lat,glathida.loc[i].lon)
        
        # find distance between selected glathida glacier and all RGI
        distances = RGI.apply(
            lambda row: geopy.distance.geodesic((row.CenLat,row.CenLon),glathida_ll),
            axis = 1
        )
        
        # find index of minimum distance between glathida and RGI glacier
        RGI_index = np.argmin(distances)
        RGI_match = RGI.loc[RGI_index]
        
        # concatonate two rows and append to dataframe with indexes for both glathida and RGI
        temp_df = pd.concat([RGI_match, glathida.loc[i]], axis = 0)
        df = df.append(temp_df, ignore_index = True)
    #     df = df.append(GlaThiDa_and_RGI, ignore_index = True)
        df['GlaThiDa_index'].iloc[-1] = i
        df['RGI_index'].iloc[-1] = RGI_index


        df.to_csv(pth_3 + 'GlaThiDa_RGI_matched_indexes_4_live.csv')

        
'''

'''
def data_loader_4(
    pth_1 = '/data/fast1/glacierml/T_models/T_data/',
    pth_2 = '/data/fast1/glacierml/T_models/RGI/rgi60-attribs/',
    pth_3 = '/data/fast1/glacierml/T_models/matched_indexes/'
):
    print('matching GlaThiDa and RGI data method 4...')
    RGI = pd.DataFrame()
    for file in os.listdir(pth_2):
        file_reader = pd.read_csv(pth_2 + file, encoding_errors = 'replace', on_bad_lines = 'skip')
        RGI = RGI.append(file_reader, ignore_index = True)

    glathida = pd.read_csv(pth_1 + 'glacier.csv')
    indexes = pd.read_csv(pth_3 + 'GlaThiDa_RGI_matched_indexes_4.csv')
    indexes = indexes.rename(columns = {
        'name':'name_g',
        'Name':'name_r',
        'area':'area_g',
        'Area':'area_r',
        'BgnDate':'date_r',
        'date':'date_g'


    })
    df = indexes[[
        'CenLat',
        'CenLon',
    #     'LAT',
    #     'LON',
        'Lmax',
        'Zmin',
        'Zmed',
        'Zmax',
        'mean_thickness',
    #     'GlaThiDa_index',
    #     'RGI_index',
        'area_g',
        'area_r',
        'Aspect',
        'Slope',
    #     'name_r',
    #     'name_g',
    #     'date_r',
    #     'date_g'
    ]]

    df['size_anomaly'] = abs(df['area_g'] - df['area_r'])
    df = df[df['size_anomaly'] < 1]
    df = df.drop([
        'size_anomaly',
        'area_g'
#         'area_r'
    ], axis = 1)
    
    df = df.rename(columns = {
        'area_r':'Area'
    })
    
    df = df.drop(df.loc[df['Zmed']<0].index)
    df = df.drop(df.loc[df['Lmax']<0].index)
    df = df.drop(df.loc[df['Slope']<0].index)
    df = df.drop(df.loc[df['Aspect']<0].index)
    df = df.reset_index()
    df = df.drop('index', axis=1)
    
    
    
    
    
    return df


'''
data_loader_5
input = path to GlaThiDa data. Default coded in. will also request regional data when run
output = dataframe containing glacier-scale GlaThiDa information with null entries dropped paired with RGI attributes and divided up by selected region. Uses the same matched index csv as data_loader_2(). 
'''
def data_loader_5(pth = '/data/fast1/glacierml/T_models/regional_data/rd1/training_data/'):
    print('matching GlaThiDa and RGI data...')
    df = pd.DataFrame()
    # data has already been matched and cleaned using python files earlier.
    # this data is broken up by region and this function allows for region selection
    for file in os.listdir(pth):
        file_reader = pd.read_csv(pth+file, encoding_errors = 'replace', on_bad_lines = 'skip')
        df = df.append(file_reader, ignore_index = True)
        df = df.drop_duplicates(subset = ['CenLat','CenLon'], keep = 'last')
        df = df[[
        #     'GlaThiDa_index',
        #     'RGI_index',
        #     'RGIId',
            'region',
        #     'geographic region',
            'CenLon',
            'CenLat',
            'Area',
            'Zmin',
            'Zmed',
            'Zmax',
            'Slope',
            'Aspect',
            'Lmax',
            'thickness'
        ]]
        
    # this prints a message that lists available regions to select.
    # entering anything other than a region that matches will cause it to creash.
    # need input verification?
    print(
        'please select region: ' + str(list(
            df['region'].unique()
        ) )
    )
    df5 = df[df['region'] == float(input())]    
#     df5 = df5.drop('region', axis=1)
    return df5




'''
data_loader_6
input = path to GlaThiDa data. Default coded in. will also request regional data when run
output = dataframe containing glacier-scale GlaThiDa information with null entries dropped paired with RGI attributes and divided up by selected region. Uses the same matched index csv as data_loader_4(). 
'''
def data_loader_6(pth = '/data/fast1/glacierml/T_models/regional_data/rd2/training_data/'):
    print('matching GlaThiDa and RGI data...')
    df = pd.DataFrame()
    
    # data has already been matched and cleaned using python files earlier.
    # this data is broken up by region and this function allows for region selection
    for file in tqdm(os.listdir(pth)):
        f = pd.read_csv(pth+file, encoding_errors = 'replace', on_bad_lines = 'skip')
        df = df.append(f, ignore_index = True)

        df = df.drop_duplicates(subset = ['CenLon','CenLat'], keep = 'last')
        df = df[[
        #     'GlaThiDa_index',
        #     'RGI_index',
        #     'RGIId',
            'region',
        #     'geographic region',
            'CenLon',
            'CenLat',
            'Area',
            'Zmin',
            'Zmed',
            'Zmax',
            'Slope',
            'Aspect',
            'Lmax',
            'thickness'
        ]]
    
    # this prints a message that lists available regions to select.
    # entering anything other than a region that matches will cause it to creash.
    # need input verification?
    print(
        'please select region: ' + str(list(
            df['region'].unique()
        ) )
    )
    df6 = df[df['region'] == float(input())]   
#     df6 = df6.drop('region', axis=1)
    return df6



            
                

    

                

                
                








'''
thickness_renamer
input = name of dataframe containing column named either 'MEAN_THICKNESS' or 'mean_thickness'
output = dataframe returned withe name changed to 'thickness'
'''
def thickness_renamer(df):
    if 'MEAN_THICKNESS' in df.columns:
        
        df = df.rename(columns = {
            'MEAN_THICKNESS':'thickness'
        },inplace = True)
        
    else:
        df = df.rename(columns = {
            'mean_thickness':'thickness'
        },inplace = True)
        
'''
data_splitter
input = name of dataframe and selected random state.
output = dataframe and series randomly selected and populated as either training or test features or labels
'''
# Randomly selects data from a df for a given random state (usually iterated over a range of 25)
# Necessary variables for training and predictions
def data_splitter(df, random_state = 0):
    train_dataset = df.sample(frac=0.8, random_state=random_state)
    test_dataset = df.drop(train_dataset.index)

    train_features = train_dataset.copy()
    test_features = test_dataset.copy()

    #define label - attribute training to be picked
    train_labels = train_features.pop('thickness')
    test_labels = test_features.pop('thickness')
    
    return train_features, test_features, train_labels, test_labels


'''
prethicktor_inputs
input = none
output = hyperparameters and layer architecture for DNN model
'''
# designed to provide a CLI to the model for each run rather modifying code
def prethicktor_inputs():
    print('This model currently supports two layer architecture. Please set neurons for first layer')
    layer_1_input = input()
    
    print('Please set neurons second layer')
    layer_2_input = input()
    
    print('Please select learning rate: 0.1, 0.01, 0.001')
    lr_list = ('0.1, 0.01, 0.001')
    lr_input = input()
    while lr_input not in lr_list:
        print('Please select valid learning rate: 0.1, 0.01, 0.001')
        lr_input = input()
        
    print('Please define epochs')
    ep_input = int(input())
    while type(ep_input) != int:
        print('Please input an integer for epochs')
        ep_input = input()
    
    print('include dropout layer? y / n')
    dropout_input = input()
    dropout_input_list = ('y', 'n')
    while dropout_input not in dropout_input_list:
        print('Please select valid input: y / n')
        dropout_input = input()
    if dropout_input == 'y':
        dropout = True
    elif dropout_input == 'n':
        dropout = False
    
    return layer_1_input, layer_2_input, lr_input, ep_input, dropout




'''
build_linear_model
input = normalized data and desired learning rate
output = linear regression model
'''
# No longer used
def build_linear_model(normalizer,learning_rate=0.1):
    model = tf.keras.Sequential([
        normalizer,
        layers.Dense(1)
    ])

    model.compile(
        optimizer=tf.optimizers.Adam(learning_rate=learning_rate),
        loss='mean_absolute_error')
    
    return model



'''
build_dnn_model
input = normalized data and selected learning rate
output = dnn model with desired layer architecture, ready to be trained.
'''
def build_dnn_model(norm, learning_rate=0.1, layer_1 = 10, layer_2 = 5, dropout = True):
    
    if dropout == True:
        model = keras.Sequential(
            [
                  norm,
                  layers.Dense(layer_1, activation='relu'),
                  layers.Dropout(rate = 0.1, seed = 0),
                  layers.Dense(layer_2, activation='relu'),

                  layers.Dense(1) 
            ]
        )

        model.compile(loss='mean_absolute_error',
                    optimizer=tf.keras.optimizers.Adam(learning_rate = learning_rate))
        
    else:
        model = keras.Sequential(
            [
                  norm,
                  layers.Dense(layer_1, activation='relu'),
                  layers.Dense(layer_2, activation='relu'),

                  layers.Dense(1) 
            ]
        )

        model.compile(loss='mean_absolute_error',
                    optimizer=tf.keras.optimizers.Adam(learning_rate = learning_rate))
        
    
    return model



'''
plot_loss
input = desired test results
output = loss plots for desired model
'''
def plot_loss(history):
#     plt.subplots(figsize=(10,5))
    plt.plot(history['loss'], label='loss')
    plt.plot(history['val_loss'], label='val_loss')
    #   plt.ylim([0, 10])
    plt.xlabel('Epoch')
    plt.ylabel('Error')
    plt.legend()
    plt.grid(True)
    

     
'''
build_and_train_model
input = dataset, desired: learning rate, validation split, epochs, random state. module and res are defined as inputs when run and determine where data is saved.
output = saved weights for trained model and model results saved as a csv
'''

def build_and_train_model(dataset,
                          learning_rate = 0.001,
                          validation_split = 0.2,
                          epochs = 300,
                          random_state = 0,
                          module = 'sm2',
                          res = 'sr2',
                          layer_1 = 10,
                          layer_2 = 5,
                          dropout = True
                         ):
    # define paths
    arch = str(layer_1) + '-' + str(layer_2)
    svd_mod_pth = 'saved_models/' + module + '/sm_' + arch + '/'
    svd_res_pth = 'saved_results/' + res + '/sr_' + arch + '/'

    # code snippet to make folders for saved models and results if they do not already exist
    isdir = os.path.isdir(svd_mod_pth)

    if isdir == False:
        os.makedirs(svd_mod_pth)

    isdir = os.path.isdir(svd_res_pth)
    if isdir == False:
        os.makedirs(svd_res_pth)


    if dropout == True:
        dropout = '1'
    elif dropout == False:
        dropout = '0'


#     split data
    (train_features,test_features,
     train_labels,test_labels) = data_splitter(dataset)
#         print(dataset.name)

#     normalize data
#         print('Normalizing ' + str(dataset.name) + ' data')
    normalizer = {}
    variable_list = list(train_features)
    for variable_name in variable_list:
        normalizer[variable_name] = preprocessing.Normalization(input_shape=[1,], axis=None)
        normalizer[variable_name].adapt(np.array(train_features[variable_name]))

    normalizer['ALL'] = preprocessing.Normalization(axis=-1)
    normalizer['ALL'].adapt(np.array(train_features))
#         print(dataset.name + ' data normalized')

#      DNN model
    dnn_model = {}
    dnn_history = {}
    dnn_results = {}

#         print(
#             'Running multi-variable DNN regression on ' + 
#             str(dataset.name) + 
#             ' dataset with parameters: Learning Rate = ' + 
#             str(learning_rate) + 
#             ', Layer Architechture = ' +
#             arch +
#             ', dropout = ' + 
#             dropout +
#             ', Validation split = ' + 
#             str(validation_split) + 
#             ', Epochs = ' + 
#             str(epochs) + 
#             ', Random state = ' + 
#             str(random_state) 
#         )

    # set up model with  normalized data and defined layer architecture
    dnn_model = build_dnn_model(normalizer['ALL'], learning_rate, layer_1, layer_2, dropout)

    # train model on previously selected and splitdata
    dnn_history['MULTI'] = dnn_model.fit(
        train_features,
        train_labels,
        validation_split=validation_split,
        verbose=0, 
        epochs=epochs
    )

    #save model, results, and history

#         print('Saving results')


    df = pd.DataFrame(dnn_history['MULTI'].history)


    df.to_csv(            
       svd_res_pth +
       str(dataset.name) +
       '_' +
       dropout +
       '_dnn_history_MULTI_' +
       str(learning_rate) +
       '_' +
       str(validation_split) +
       '_' +
       str(epochs) +
       '_' +
       str(random_state)

    )

    dnn_model.save(
        svd_mod_pth + 
        str(dataset.name) + 
        '_' +
        dropout +
        '_dnn_MULTI_' + 
        str(learning_rate) + 
        '_' + 
        str(validation_split) + 
        '_' + 
        str(epochs) + 
        '_' + 
        str(random_state)
    )
#         print('model training complete')
#         print('')
        
        



