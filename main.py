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

with open('./data/etab.json') as f:
    etab = json.load(f)
with open('./data/params.json') as f:
    params = json.load(f)

statements = load_statements(
    '../open-student-environment/data'
    '/statements-brneac3-20180301-20180531'
    '.json')
agents = load_agents(
    '../open-student-environment/data'
    '/accounts-brneac3-0-20180630.json')

env = Environment(agents, statements)
nodes, adjancy = env.nodes, env.structure

active_agents = get_active_agents(statements)
nodes, adjancy = filter_by_users(nodes, adjancy, active_agents)

etab = [e for e in etab if e['numero_uai'] in nodes]

nodes = [{'name': str(n), 'type': nodes[n]} for children in adjancy.values()
         for n in children]
for node in nodes:
    if node['name'] not in adjancy:
        adjancy[node['name']] = []

adjancy = {k: list(v) for k, v in adjancy.items()}


def generate_distrib():
    mn = np.random.randint(40, 100)
    std = np.random.randint(10, 20)
    return list(map(to_scalar, np.random.normal(mn, std,
                                                len(nodes))))


def to_scalar(l):
    return np.asscalar(l)


def get_hist(p_val, cont):
    if cont == "discrete":
        t = np.histogram(p_val, bins=1000)
    else:
        t = np.histogram(p_val, bins=1000, density=True)
    return {'values': list(map(to_scalar, list(t[0]))),
            'bins': list(map(to_scalar, list(t[1])))}


node_params = defaultdict(dict)
params_dist = {k: {'dist': list(generate_distrib())} for k in params.keys()}

for p_key, p_val in params_dist.items():
    params_dist[p_key]['hist'] = get_hist(p_val['dist'], params[p_key])
    params_dist[p_key]['max'] = max(p_val['dist'])
    params_dist[p_key]['min'] = min(p_val['dist'])
    assign = np.random.choice(p_val['dist'], len(nodes), replace=False)
    del (params_dist[p_key]['dist'])
    for a, n in enumerate(nodes):
        node_params[n['name']] = {'min': params_dist[p_key]['min'],
                                  'max': params_dist[p_key]['max'],
                                  'value': assign[a]
                                  }


class GetParametersNames(Resource):
    def get(self):
        return list(params_dist.keys())


class GetNodes(Resource):
    def get(self):
        return nodes


class GetAdjancy(Resource):
    def get(self):
        return adjancy


class GetEtab(Resource):
    def get(self):
        return etab


class GetPamaters(Resource):
    def get(self):
        return params_dist


class GetNodeParameters(Resource):
    def get(self):
        args = parser.parse_args()
        return node_params[args['node-name']]


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
