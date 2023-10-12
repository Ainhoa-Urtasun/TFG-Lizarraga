import requests
import json
import pandas
import geopandas
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import pyproj
import warnings
warnings.filterwarnings("ignore")

fixed = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/'
url = '{}{}'.format(fixed,'lfsa_ehomp')
metadata = requests.get(url).json()
print(metadata['label'])
data = pandas.Series(metadata['value']).rename(index=int).sort_index()
n = 1 # Initialize the result to 1
for num in metadata['size']:
  n *= num
data = data.reindex(range(0,n),fill_value=0)
structure = [pandas.DataFrame({key:val for key,val in metadata['dimension'][dim]['category'].items()}).sort_values('index')['label'].values for dim in metadata['id']]
data.index = pandas.MultiIndex.from_product(structure,names=metadata['id'])
mydata = data.reset_index()
mydata = mydata[mydata.wstatus=='Employed persons']
mydata = mydata[mydata.sex=='Total']
mydata = mydata[mydata.age=='From 20 to 64 years']
mydata = mydata[mydata.frequenc=='Usually']
mydata = mydata[['geo','time',0]]
mydata.rename(columns={'geo':'ADMIN'},inplace=True)
mydata.rename(columns={0:'percentage'},inplace=True)

world = geopandas.read_file('/content/TFG-Lizarraga/ne_110m_admin_0_countries.zip')[['ADMIN','geometry']]
polygon = Polygon([(-25,35),(40,35),(40,75),(-25,75)])
europe = geopandas.clip(world,polygon)

mydata1 = mydata[mydata.time=='2022']
table = mydata.pivot(index='ADMIN',columns='time',values=['percentage']).reset_index()
table.columns = table.columns.droplevel(level=0)
table.rename(columns={'ADMIN':'GEO'},inplace=True)
table = table.rename_axis(columns=None)

mydata1 = mydata1.merge(europe,on='ADMIN',how='right')
mydata1 = geopandas.GeoDataFrame(mydata1,geometry='geometry')
fig,ax = plt.subplots(1,figsize=(10,10))
mydata1.plot(column='percentage',alpha=0.8,cmap='cool',ax=ax,legend=True)
ax.set_title('Employed persons usually working from home from 20 to 64 years\nas a percentage of total employment (source: Eurostat)')
ax.axis('off')
