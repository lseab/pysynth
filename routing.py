from copy import copy
from filters import FreqModulationFilter

class Routing:

    def __init__(self, oscillators):
        self.oscillators = oscillators
        self.nodes = []
        self.operations = []
        self.freq_mod = None

    def freq_modulate(self, source, modulator):
        return FreqModulationFilter(source=source, modulator=modulator)

    def get_nodes(self):
        return [o.osc for o in self.oscillators if not o.to_oscillator]

    def get_parents(self, node):
        parents = {}   
        parents[node] = []
        for o in self.oscillators:
            for i in range(len(o.to_oscillator)):
                if o.to_oscillator and o.to_oscillator[i].osc == node:
                    parents[node].append(o.osc)
        return [n for n in parents[node]]

    def do_walk(self, nodes):
        for n, node in enumerate(nodes):
            node_dict = {}
            node_dict[node] = self.get_parents(node)
            nodes[n] = node_dict
            if len(nodes[n][node]) > 0: 
                self.do_walk(nodes[n][node])
        return nodes

    def establish_route(self):
        nodes = self.get_nodes()
        return self.do_walk(nodes)

    def do_routing(self, route, prev=None):
        for el in route:
            for k in list(el.keys()):
                if len(el[k]) == 0:
                    self.freq_mod = self.freq_modulate(k, prev)
                    route.remove(el)
                else:
                    self.do_routing(el[k], k)
                    if len(el[k]) != 0:
                        self.do_routing(el[k], k)
                    el[self.freq_mod] = []
                    del el[k]
        return route

    def get_final_output(self):
        route = self.establish_route()
        final_output = self.do_routing(route)
        return final_output