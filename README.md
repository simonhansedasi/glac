# glacier_prethicktor
A machine learning approach to predicting glacier thicknesses.

We treat estimating glacier thickness as a regression problem as opposed to ice velocity flow models. We train machine learning models with Glacier Thickness Database thickness measurements as an independent variable co-registered with surface attributes from the Randolph Glacier Inventory as dependent variables to estimate thickness.
## Requirements
<ul>
    <li> python 3.8.10
    <li> tensorflow v. 2.12.0
</ul>

### Install conda environment with the following code snippet
```
conda install -n glacierml python=3.8.10
conda activate glacierml
pip install ipykernel
python -m ipykernel install --user --name=prethicktor --display-name="glacierml (Python3.8.10)"
```

Run the notebooks in number order. The rest are for data analysis.

<!-- 00-install_packages.ipynb will install the rest of the project dependencies.

01-acquire_data.ipynb will create a project directory from a set path and will download both RGI v. 6.0 glacier attributes and GlaThiDa v. 3.1.0, as well as extract the necessary data files. 

02-match_glacier_centroids.ipynb matches GlaThiDa glacier centroid latitude and longitude to the nearest match in RGI and saves a data file for coregistering data.

1-coregistration_testing.ipynb is the notebook used to test coregistration methods.
2-LOO_archtesting.ipynb tests a few different neuron combinatiosn
3-LOO_archselection.ipynb sorts through the models created in the previous notebook and ranks the models by loss and number of parameters
4-LOO.ipynb employs leave one out cross validation and runs a regression analysis
5-LOO_analysis.ipynb digs into the results and data from the previous notebook. -->