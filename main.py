import pandas as pd
from networkx import DiGraph
from vrpy import VehicleRoutingProblem
import requests

orders = pd.read_excel('Service_Deal_Order Sample.xlsx',
                       usecols=['Id', 'OrderAmount', 'FactoryLocationLat', 'FactoryLocationLon',
                                'BakeryLocationLat', 'BakeryLocationLon']).to_dict(orient='records')


def calculateCostWithTime(originLat, originLon, destinationLat, destinationLon):
    url = f'https://api.neshan.org/v1/distance-matrix?type=car&origins={originLat},{originLon}' \
          f'&destinations={destinationLat},{destinationLon}'
    response = requests.get(url, headers={'Api-Key': 'service.8e2e6ea4da51455b90bc163e10223277'})
    return response.json()['rows'][0]['elements'][0]['duration']['value']


def calculateCostWithDistance(originLat, originLon, destinationLat, destinationLon):
    url = f'https://api.neshan.org/v1/distance-matrix?type=car&origins={originLat},{originLon}' \
          f'&destinations={destinationLat},{destinationLon}'
    response = requests.get(url, headers={'Api-Key': 'service.8e2e6ea4da51455b90bc163e10223277'})
    return response.json()['rows'][0]['elements'][0]['distance']['value']


def calculateCost(originLat, originLon, destinationLat, destinationLon):
    return calculateCostWithTime(originLat, originLon, destinationLat, destinationLon)
    # return ((destinationLat - originLat) ** 2 + (destinationLon - originLon) ** 2) ** 0.5


def getDemandWithId(orderId):
    for order in orders:
        if order['Id'] == orderId:
            return order["OrderAmount"]


G = DiGraph()
for nodeOrigin in orders:
    G.add_edge("Source", nodeOrigin['Id'],
               cost=calculateCost(nodeOrigin['FactoryLocationLat'], nodeOrigin['FactoryLocationLon'],
                                  nodeOrigin['BakeryLocationLat'], nodeOrigin['BakeryLocationLon']))
    G.add_edge(nodeOrigin['Id'], "Sink",
               cost=calculateCost(nodeOrigin['BakeryLocationLat'], nodeOrigin['BakeryLocationLon'],
                                  nodeOrigin['FactoryLocationLat'], nodeOrigin['FactoryLocationLon']))
    for nodeDestination in orders:
        if nodeOrigin['Id'] != nodeDestination['Id']:
            G.add_edge(nodeOrigin['Id'], nodeDestination['Id'],
                       cost=calculateCost(nodeOrigin['BakeryLocationLat'], nodeOrigin['BakeryLocationLon'],
                                          nodeDestination['BakeryLocationLat'], nodeDestination['BakeryLocationLon']))
for v in G.nodes():
    if v not in ["Source", "Sink"]:
        G.nodes[v]["demand"] = getDemandWithId(v)
prob = VehicleRoutingProblem(G)
prob.load_capacity = 400
prob.solve()
print(prob.best_routes)
print(prob.best_routes_cost)
