import pandas as pd
flows = pd.read_csv('/home/ba0100063c/Descargas/simple_fruit_sales.csv')
flows
from ipysankeywidget import SankeyWidget
SankeyWidget(links=flows.to_dict('records'))


from floweaver import *

# Set the default size to fit the documentation better.
size = dict(width=570, height=300)

nodes = {
    'farms': ProcessGroup(['farm1', 'farm2', 'farm3',
                           'farm4', 'farm5', 'farm6']),
    'customers': ProcessGroup(['James', 'Mary', 'Fred', 'Susan']),
}

ordering = [
    ['farms'],       # put "farms" on the left...
    ['customers'],   # ... and "customers" on the right.
]

bundles = [
    Bundle('farms', 'customers'),
]

sdd = SankeyDefinition(nodes, bundles, ordering)
weave(sdd, flows).to_widget(**size)