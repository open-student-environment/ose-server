import json
from flask_cors import CORS
from flask import Flask
from flask_restful import Resource, Api, reqparse
from ose.statement import load_statements
from ose.agent import load_agents
from ose.environment import Environment, get_active_agents, filter_by_users
import numpy as np
from collections import defaultdict
import datetime

app = Flask(__name__)
api = Api(app)
cors = CORS(app, origin="*")
parser = reqparse.RequestParser()
parser.add_argument('node-name', type=str, help='The name of the the '
                                                'requested nodes')
parser.add_argument('context', type=bool, store_missing=True, help='Does the '
                                                                   'context'
                                                                   'appears '
                                                                   'on node '
                                                                   'parameters')

with open('./data/etab.json') as f:
    etab = json.load(f)
with open('./data/params.json') as f:
    _params = json.load(f)

statements = load_statements(
    '../open-student-environment/data'
    '/statements-brneac3-20180301-20180531'
    '.json')
agents = load_agents(
    '../open-student-environment/data'
    '/accounts-brneac3-0-20180630.json')

env = Environment(agents, statements)
nodes, adjacency = env.nodes, env.structure

active_agents = get_active_agents(statements)#[:100])
nodes_filtered = ["804f411c-ecf7-4ba7-b0d9-eb162b8ec1e1",
                  "55db4891-9ea6-4c5d-b55d-2063f815d90d"]
nodes, adjacency = filter_by_users(nodes, adjacency, active_agents)

etab = [e for e in etab if e['numero_uai'] in nodes]

def generate_name():
    return "aaaa"

def create_nodes(adj, nds):
    def create_node_description(n, typ):
        if typ == 'groupe':
            return {
                'id': str(n),
                'type': typ,
                'name': "groupe {}".format(str(n))
            }
        else:
            return {
                'id': str(n),
                'type': typ,
                'name': generate_name(),
                'indicators':  {}
            }

    nds = [create_node_description(n, nds[n]) for children in
           adj.values()
           for n in children]
    for nd in nds:
        if nd['name'] not in adj:
            adj[nd['name']] = []
    adj = {k: list(v) for k, v in adj.items()}
    return nds, adj


nodes, adjacency = create_nodes(adjacency, nodes)


def generate_distrib(n):
    mn = np.random.randint(40, 100)
    std = np.random.randint(10, 20)
    return list(map(np.asscalar, np.random.normal(mn, std,
                                                  n)))

def get_hist(p_val, cont):
    if cont == "discrete":
        t = np.histogram(p_val, bins=1000)
    else:
        t = np.histogram(p_val, bins=1000, density=True)
    return {'values': list(map(np.asscalar, list(t[0]))),
            'bins': list(map(np.asscalar, list(t[1])))}

node_params = defaultdict(dict)
params_dist = {k: {'dist': list(generate_distrib(len(nodes)))} for k in
               _params.keys()}

for p_key, p_val in params_dist.items():
    params_dist[p_key]['hist'] = get_hist(p_val['dist'], _params[p_key])
    params_dist[p_key]['max'] = max(p_val['dist'])
    params_dist[p_key]['min'] = min(p_val['dist'])
    assign = np.random.choice(p_val['dist'], len(nodes), replace=False)
    del (params_dist[p_key]['dist'])
    for a, n in enumerate(nodes):
        # node_params[n['name']][p_key] = {'min': params_dist[p_key]['min'],
        #         #                                  'max': params_dist[p_key]['max'],
        #         #                                  'value': (assign[a] -
        #         #                                            params_dist[p_key][
        #         #                                                'min']) * 100 / (
        #         #                                                   params_dist[
        #         #                                                       p_key][
        #         #                                                       'max'] -
        #         #                                                   params_dist[
        #         #                                                       p_key][
        #         #                                                       'min']),
        #         #                                  'raw': assign[a]
        #         #                                  }
        if n['type'] != 'groupe':
            n['indicators'][p_key] = assign[a]

class GetParametersNames(Resource):
    def get(self):
        return list(params_dist.keys())


class GetNodes(Resource):
    def get(self):
        return nodes


class GetAdjancy(Resource):
    def get(self):
        return adjacency


class GetEtab(Resource):
    def get(self):
        return etab


def get_format(name, params):
    def create_dict(a, b):
        return {'name': a, 'value': b}

    resp = {}
    resp['name'] = name
    resp['type'] = _params[name]
    resp['series'] = [create_dict(a, b) for a, b in zip(params['hist']['bins'],
                                                        params[
                                                            'hist'][
                                                            'values'])]
    return resp


class GetPamaters(Resource):
    def get(self):
        resp = [get_format(k, v) for k, v in params_dist.items()]
        return resp


def get_formatted_params(name, params):
    resp = {'name': name,
            'value': params['value']
            }
    return resp


class GetNodeParameters(Resource):
    def get(self):
        args = parser.parse_args()
        resp = {}
        if args['context']:
            resp['context'] = [get_format(k, v) for k, v in
                               params_dist.items()]
        if node_params[args['node-name']]:
            resp['name'] = 'node-parameters'
            resp['series'] = [get_formatted_params(k, p) for k, p in
                              node_params[args['node-name']].items()]
        return resp


def convert_timestamp_to_datetime(activity):
    if activity is None:
        return None
    if type(activity['timestamp']) != str:
        activity['timestamp'] = datetime.datetime.utcfromtimestamp(activity[
                                                                       'timestamp']
                                                                   ).strftime(
            '%Y-%m-%d %H:%M:%S')
    return activity


def convert_timestamp_to_datetime_formatted(activity):
    if activity is None:
        return None
    if type(activity['timestamp']) != str:
        activity['timestamp'] = datetime.datetime.utcfromtimestamp(activity[
                                                                       'timestamp']
                                                                   ).strftime(
            '%Y-%m-%d %H:%M:%S')
    return activity['timestamp']


class GetNodeActivityFormatted(Resource):
    def get(self):
        args = parser.parse_args()
        x = list(map(convert_timestamp_to_datetime,
                     env._statements[args['node-name']]))
        y = len(x) * [1]
        resp = {'x': x,
                'y': y,
                'type': 'scatter'}
        return resp


class GetNodeActivity(Resource):
    def get(self):
        args = parser.parse_args()
        return list(map(convert_timestamp_to_datetime,
                        env._statements[args['node-name']]))


api.add_resource(GetNodes, '/nodes')
api.add_resource(GetAdjancy, '/adjancy')
api.add_resource(GetEtab, '/etab')
api.add_resource(GetParametersNames, '/model')
api.add_resource(GetPamaters, '/model/parameters')
api.add_resource(GetNodeParameters, '/nodes/parameters')
api.add_resource(GetNodeActivity, '/nodes/activity')

if __name__ == '__main__':
    app.run(debug=True)
