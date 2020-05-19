from copy import copy
from filters import FreqModulationFilter, SumFilter

class Routing:

    def __init__(self, oscillators):
        self.oscillators = oscillators
        self.nodes = []
        self.operations = []
        self.freq_mod = None

    def freq_modulate(self, source, modulator):
        return FreqModulationFilter(source=source, modulator=modulator)

    def sum_signals(self, signals):
        return SumFilter(signals)

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
                    if prev != None:
                        self.freq_mod = self.freq_modulate(prev, k)
                        route.remove(el)
                elif len(el[k]) > 1:
                    self.do_routing(el[k])
                    iter_ = iter(el[k])
                    summed = SumFilter([next(iter(o.keys())) for o in el[k]])
                    freq_mod = self.freq_modulate(k, summed)
                    el[freq_mod] = []
                    del el[k]
                else:
                    self.do_routing(el[k], k)
                    if len(el[k]) != 0:
                        self.do_routing(el[k], k)
                    el[self.freq_mod] = []
                    del el[k]
        return route

    def get_final_output(self):
        final_output = []
        routes = self.establish_route()
        for route in routes:
            routed = self.do_routing([route])
            final_output.append([next(iter(o.keys())) for o in routed][0])
        return final_output