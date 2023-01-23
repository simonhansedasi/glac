import pandas as pd
import numpy as np
import glacierml as gl
from tqdm import tqdm
import tensorflow as tf
import warnings
from tensorflow.python.util import deprecation
import os
import logging
tf.get_logger().setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
deprecation._PRINT_DEPRECATION_WARNINGS = False
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
pd.set_option('mode.chained_assignment', None)
import configparser

tf.random.set_seed(42)
# chosen_parameterization = input()   
    
parameterization = str(  3  )
para = 2
config = configparser.ConfigParser()
config.read('model_parameterization.ini')

data = gl.load_training_data(
    root_dir = '/home/prethicktor' + parameterization + '/data/',
    RGI_input = config[parameterization]['RGI_input'],
    scale = config[parameterization]['scale'],
    area_scrubber = config[parameterization]['area scrubber'],
    anomaly_input = float(   config[parameterization]['size anomaly']   )
)
data = data.drop(
    data[data['distance test'] >= float(  config[parameterization]['distance test']  )].index
)

data = data.drop([
    'RGIId','region', 'RGI Centroid Distance', 
    'AVG Radius', 'Roundness', 
        'distance test', 
    'size difference'
], axis = 1)



RS = range(0,25,1)
# print('')
# print(data.name)
print(data)  
#     print(len(dataset))

#     ep_input = '2000'
layer_1_list = [3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
layer_2_list = [2,3,4,5,6,7,8,9,10,11,12,13,14,15]
#     lr_input = '0.01'

for layer_2_input in (layer_2_list):
    for layer_1_input in (layer_1_list):
        if layer_1_input <= layer_2_input:
            pass
        elif layer_1_input > layer_2_input:

            arch = str(layer_1_input) + '-' + str(layer_2_input)
            dropout = True
            print('')
            print('Running multi-variable DNN regression with parameterization ' + 
                str(parameterization) + 
                ', layer architecture = ' +
                arch)

            for rs in tqdm(RS):
        #             for lr in LR:

                gl.build_and_train_model(
                    data, 
                    random_state = rs, 
                    parameterization = parameterization, 
                    res = parameterization,
                    layer_1 = layer_1_input,
                    layer_2 = layer_2_input,
                )   

            
model_predictions = pd.DataFrame()
model_statistics = pd.DataFrame()
# dropout_input = dropout_input_iter
rootdir = 'saved_models/' + parameterization + '/'

print('loading and evaluating models...')
for arch in tqdm( os.listdir(rootdir)):       
#     print('layer architecture: ' + arch[3:])
    pth = os.path.join(rootdir, arch)
    for folder in (os.listdir(pth)):
        architecture = arch
#         print(architecture)
        model_loc = (
            rootdir + 
            arch + 
            '/' + 
            folder
        )

        model_name = folder
        dnn_model = gl.load_dnn_model(model_loc)
#         print(dnn_model)
        df = gl.evaluate_model(architecture, model_name, data, dnn_model, parameterization)

        model_predictions = pd.concat([model_predictions, df], ignore_index = True)
#     break
# print(model_predictions['architecture'])
# print(list(model_predictions))
model_predictions.rename(columns = {0:'avg train thickness'},inplace = True)
model_predictions.to_csv('zults/model_predictions_' + parameterization + '.csv')
# calculate statistics
print('calculating statistics...')
dnn_model = {}

for arch in tqdm(list(model_predictions['layer architecture'].unique())):
    model_thicknesses = model_predictions[model_predictions['layer architecture'] == arch]


    model_name = ('0')

    model_loc = (
        rootdir + 
        arch + 
        '/' +
        '0'
    )
#     print(model_loc)
    isdir = os.path.isdir(model_loc)
#     print(isdir)
    if isdir == False:
        print('model not here, calculating next model')
    elif isdir == True:
        
        
        dnn_model = gl.load_dnn_model(model_loc)
        df = gl.calculate_model_avg_statistics(
            dnn_model,
            arch,
            data,
            model_thicknesses
        )

        model_statistics = pd.concat(
            [model_statistics, df], ignore_index = True
        )
        #         print(list(model_statistics))
    
    
model_statistics['architecture weight 1'] = (
    sum(model_statistics['test mae avg']) / model_statistics['test mae avg']
)
model_statistics['architecture weight 2'] = (
    model_statistics['test mae avg'] / sum(model_statistics['test mae avg'])
)
model_statistics.to_csv(
    'zults/model_statistics_' + 
    parameterization + 
    '.csv'
)

model_statistics = pd.read_csv('zults/model_statistics_' + parameterization + '.csv')
# deviations_2 = pd.read_csv('zults/deviations_' + dataset.name + '_0.csv')
# deviations = pd.concat([deviations_1, deviations_2])
model_statistics = model_statistics.reset_index()
# print(list(model_statistics))

model_statistics = model_statistics[[
'layer architecture',
# 'model parameters',
# 'total inputs',
# 'test mae avg',
# 'train mae avg',
# 'test mae std dev',
# 'train mae std dev'
]]

print('Estimating thicknesses...')

for index in (model_statistics.index):
#     print(index)
#     print(model_statistics.iloc[index])
    arch = model_statistics['layer architecture'].iloc[index]

# arch = '3-2'
    print('Estimating thicknesses with parameterization ' + parameterization + ', layer architecture = ' + arch )
    for region_selection in tqdm(range(1,20,1)):
        RGI = gl.load_RGI(
            pth = '/home/prethicktor/data/RGI/rgi60-attribs/',
            region_selection = int(region_selection)
        )
        if len(str(region_selection)) == 1:
            N = 1
            region_selection = str(region_selection).zfill(N + len(str(region_selection)))
        else:
            region_selection = region_selection

        RGI['region'] = RGI['RGIId'].str[6:8]
        RGI = RGI.reset_index()
        RGI = RGI.drop(['RGIId', 'region', 'index'], axis=1)
#         print(RGI)
        
    #         print(region_selection)
    #             if region_selection != '19':
    #                 drops = RGI[
    #                     ((RGI['region'] == str(region_selection)) & (RGI['Zmin'] < 0)) |
    #                     ((RGI['region'] == str(region_selection)) & (RGI['Zmed'] < 0)) |
    #                     ((RGI['region'] == str(region_selection)) & (RGI['Zmax'] < 0)) |
    #                     ((RGI['region'] == str(region_selection)) & (RGI['Slope'] < 0)) |
    #                     ((RGI['region'] == str(region_selection)) & (RGI['Aspect'] < 0))
    #                 ].index
    #                 print(drops)
    #                 if not drops.empty:
    #                     print('dropping bad data')
    #                     RGI = RGI.drop(drops)
#         if 'Roundness' in dataset:
#     #         RGI['Area'] = RGI['Area'] * 1e6
#             RGI['AVG Radius'] = np.sqrt((RGI['Area'] * 1e6) / np.pi)
#             RGI['Roundness'] = (RGI['AVG Radius']) / (RGI['Lmax'])
#             RGI['Area'] = np.log(RGI['Area'] * 1e3)
#     #         RGI['Area'] = RGI['Area'] / 1e6
#             RGI_for_predictions = RGI.drop(['region', 'RGIId', 'AVG Radius'], axis = 1)
#         elif 'Roundness' not in dataset:
#             RGI_for_predictions = RGI.drop(['region', 'RGIId'], axis = 1)
# #         print(RGI_for_predictions)



        dnn_model = {}
        rootdir = 'saved_models/' + parameterization + '/'
        RS = range(0,0,1)
        dfs = pd.DataFrame()
#         for rs in (RS):
        rs = str(0)

    # each series is one random state of an ensemble of 25.
    # predictions are made on each random state and appended to a df as a column
        model = (
            rs
        )

        model_path = (
            rootdir + arch + '/' + str(rs)
        )
        results_path = 'saved_results/' + parameterization + '/' + arch + '/'

        history_name = (
            rs
        )

        dnn_history ={}
        dnn_history[rs] = pd.read_csv(results_path + rs)

        if abs((
            dnn_history[history_name]['loss'].iloc[-1]
        ) - dnn_history[history_name]['val_loss'].iloc[-1]) >= 3:

            pass
        else:

            dnn_model = tf.keras.models.load_model(model_path)

            s = pd.Series(
                dnn_model.predict(RGI, verbose=0).flatten(), 
                name = rs
            )

            dfs[rs] = s


        # make a copy of RGI to add predicted thickness and their statistics
        RGI_prethicked = RGI.copy() 
        RGI_prethicked['avg predicted thickness'] = 'NaN'
        RGI_prethicked['predicted thickness std dev'] = 'NaN'
        RGI_prethicked = pd.concat([RGI_prethicked, dfs], axis = 1)

    #         print('calculating average thickness across random state ensemble...')
        # loop through predictions df and find average across each ensemble of 25 random states
        for i in (dfs.index):
            RGI_prethicked['avg predicted thickness'].loc[i] = np.mean(dfs.loc[i])


    #         print('computing standard deviations and variances for RGI predicted thicknesses')
        # loop through predictions df and find std dev across each ensemble of 25 random states
        for i in (dfs.index):
            RGI_prethicked['predicted thickness std dev'].loc[i] = np.std(dfs.loc[i])
    #         print(' ')

        RGI_prethicked.to_csv(
            'zults/RGI_predicted_' +
            parameterization + '_' + arch + '_' + str(region_selection) + '.csv'          
        )    
        break



print('Gathering architectures...')
arch_list = gl.list_architectures(parameterization = parameterization)
arch_list = arch_list.reset_index()
arch_list = arch_list.drop('index', axis = 1)

df = pd.DataFrame(columns = {
        'RGIId','0', '1', '2', '3', '4', '5', '6', '7', '8', '9','10',
        '11','12','13','14','15','16','17','18','19','20','21',
        '22','23','24',
})
# df = pd.merge(df, arch_list, on = 'RGIId', how = 'inner')
print(arch_list)
arch_list = arch_list.sort_values('layer architecture')
# print(len(arch_list['architecture'].unique()))
# print(arch_list['architecture'].unique())
print('Architectures listed')
# print(list(predictions))
# print(predictions['architecture'].unique())
print('Compiling predictions...')
for arch in tqdm(arch_list['layer architecture'].unique()):
#     print(arch)
#     break
#     idx = index
#     print(idx)

#     coregistration =  arch_list['coregistration'].iloc[idx]
#     architecture = '_' + arch_list['architecture'].iloc[idx]
    df_glob = gl.load_global_predictions(
        parameterization = parameterization,
        architecture = arch,
    )
    

    df = pd.concat([df,df_glob])
#     print(df)
# print(df)
statistics = pd.DataFrame()
for file in (os.listdir('zults/')):
    if 'statistics_' + parameterization in file:
        file_reader = pd.read_csv('zults/' + file)
        statistics = pd.concat([statistics, file_reader], ignore_index = True)

#     print(file)
#     break
# deviations = deviations.dropna()
# print(list(statistics))
# statistics = statistics.rename(columns = {'layer architecture':'architecture'}, inplace = True)

df = pd.merge(df, statistics, on = 'layer architecture')
# df = pd.merge(df, statistics, on = 'architecture')


df = df[[
        'RGIId','0', '1', '2', '3', '4', '5', '6', '7', '8', '9','10',
        '11','12','13','14','15','16','17','18','19','20','21',
        '22','23','24','architecture weight 1'
]]

compiled_raw = df.groupby('RGIId')[
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9','10',
        '11','12','13','14','15','16','17','18','19','20','21',
        '22','23','24','architecture weight 1'
]

print('Predictions compiled')
print('Aggregating statistics...')
dft = pd.DataFrame()
for this_rgi_id, obj in tqdm(compiled_raw):
    rgi_id = pd.Series(this_rgi_id, name = 'RGIId')
#     print(f"Data associated with RGI_ID = {this_rgi_id}:")
    dft = pd.concat([dft, rgi_id])
    dft = dft.reset_index()
    dft = dft.drop('index', axis = 1)
    
    
    obj['weight'] = obj['architecture weight 1'] + 1 / (obj[['0', '1', '2', '3', '4',
                                                     '5', '6', '7', '8', '9',
                                                     '10','11','12','13','14',
                                                     '15','16','17','18','19',
                                                     '20','21','22','23','24']].var(axis = 1))
    
    
    obj['weighted mean'] = obj['weight'] * obj[['0', '1', '2', '3', '4',
                                               '5', '6', '7', '8', '9',
                                               '10','11','12','13','14',
                                               '15','16','17','18','19',
                                               '20','21','22','23','24']].mean(axis = 1)
    
    
    weighted_glacier_mean = sum(obj['weighted mean']) / sum(obj['weight'])

    
    stacked_object = obj[[
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9','10',
        '11','12','13','14','15','16','17','18','19','20','21',
        '22','23','24',
    ]].stack()
    
    glacier_count = len(stacked_object)
#     dft.loc[dft.index[-1], 'Weighted Mean Thickness'] = weighted_glacier_mean
    dft.loc[dft.index[-1], 'Mean Thickness'] = stacked_object.mean()
    dft.loc[dft.index[-1], 'Median Thickness'] = stacked_object.median()
    dft.loc[dft.index[-1],'Thickness Std Dev'] = stacked_object.std()
    
    statistic, p_value = shapiro(stacked_object)    
    dft.loc[dft.index[-1],'Shapiro-Wilk statistic'] = statistic
    dft.loc[dft.index[-1],'Shapiro-Wilk p_value'] = p_value

    
    q75, q25 = np.percentile(stacked_object, [75, 25])    
    dft.loc[dft.index[-1],'IQR'] = q75 - q25 
    
    lower_bound = np.percentile(stacked_object, 50 - 34.1)
    median = np.percentile(stacked_object, 50)
    upper_bound = np.percentile(stacked_object, 50 + 34.1)
    
    dft.loc[dft.index[-1],'Lower Bound'] = lower_bound
    dft.loc[dft.index[-1],'Upper Bound'] = upper_bound
    dft.loc[dft.index[-1],'Median Value'] = median
    dft.loc[dft.index[-1],'Total estimates'] = glacier_count
    
dft = dft.rename(columns = {
    0:'RGIId'
})
dft = dft.drop_duplicates()
dft.to_csv(
    'predicted_thicknesses/sermeq_aggregated_bootstrap_predictions_coregistration_' + 
    parameterization + '.csv'
          )