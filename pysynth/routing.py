from copy import copy
from collections import ChainMap
from pysynth.filters import FreqModulationFilter, SumFilter

class Routing:
    """
    For a given set of oscillators, the Routing object creates the FM data pipeline.
    """
    def __init__(self, oscillators):
        self.oscillators = oscillators

    def freq_modulate(self, source, modulator):
        return FreqModulationFilter(source=source, modulator=modulator)

    def sum_signals(self, signals):
        return SumFilter(signals)

    def get_carriers(self):
        """
        Returns the list of carrier oscillators in self.oscillators
        i.e. they are output oscillators and do not modulate another oscillator.
        """
        return [o for o in self.oscillators if not o.source.to_oscillators]

    def get_parents(self, node):
        """
        For a given oscillater, get list of the nodes that modulate it.
        """
        parents = []
        for o in self.oscillators:
            for i in range(len(o.source.to_oscillators)):
                if o.source.to_oscillators and o.source.to_oscillators[i] == node.source:
                    parents.append(o)
        return parents

    def get_mod_tree(self, nodes):
        """
        Recursive method to generate a modulation tree.
        Returns a nested dictionary where each key is an oscillator whose value
        is a dictionary of its modulating 'parents'.

        For instance, parallel routing will return a dictionary with the following form:

        {<Oscillator A>: {}, <Oscillator B>: {}, <Oscillator C>: {}, <Oscillator D>: {}}

        Stacked routing will return a dictionary with the following form:

        {<Oscillator A>: {<Oscillator B>: {<Oscillator C>: {<Oscillator D>: {}}}}}
        """
        for n, node in enumerate(nodes):
            node_dict = {}
            node_dict[node] = self.get_parents(node)
            nodes[n] = node_dict
            if len(nodes[n][node]) > 0: 
                self.get_mod_tree(nodes[n][node])
            nodes[n][node] = dict(ChainMap(*nodes[n][node]))
        return dict(ChainMap(*nodes))

    def do_routing(self, tree):
        """
        Iterative function to establish the frequency modulation algorithm.
        Recursively traverses a nested list of oscillators until it finds an oscillator
        whose modulating 'parents' are themselves unmodulated. The signals from the parents
        are then summed, and the node is replaced by an FM object with the node and its summed 
        parent signals (or single parent signal) as inputs.

        For instance, parallel routing will return the following object:

        [<Oscillator D>, <Oscillator C>, <Oscillator B>, <Oscillator A>]

        Stacked routing will return the following object:
        
        FreqMod(<Oscillator D>, FreqMod(<Oscillator C>, FreqMod(<Oscillator B>, <Oscillator A>)))
        """
        for node, parents in tree.items():
            if len(parents.keys()) > 0:
                self.do_routing(parents)
                if len(parents.keys()) > 1:
                    freq_mod = self.freq_modulate(node, SumFilter(parents.keys()))
                else: freq_mod = self.freq_modulate(node, next(iter(parents.keys())))
                del tree[node]
                tree[freq_mod] = {}
        return list(tree.keys())

    def get_final_output(self):
        carriers = self.get_carriers()
        tree = self.get_mod_tree(carriers)
        return self.do_routing(tree)