import pandas as pd
#from plotly.utils import pandas

flows = pd.read_csv('simple_fruit_sales.csv')
flows
from ipysankeywidget import SankeyWidget
SankeyWidget(links=flows.to_dict('records'))

