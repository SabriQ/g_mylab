#graph utils used in Jiminez et al., 2020
import sys
import itertools
import numpy as np
import networkx as nx
import pandas as pd
from networkx.algorithms.approximation import clique
from matplotlib.pylab import plt
from mylab.ana.miniscope.Mquality import * # for shuffle


def compute_correlated_pair_ratio(arr,threshold=0.3):

    """
    compute correlated_pair_ratio for each neuron by shuffle
    **Significantly correlated pairs of neurons** were defined based on
    the correlation coefficients of Ca2+ transient events within one
    second time bins during context exploration.
    """
    arr_cor = np.corrcoef(arr)
    # shuffle_cor = shuffle_corrcoef(arr)
    rows2,cols2 = np.where(arr_cor>threshold)
    correlated_pairs_index = [(row,col) for row,col in zip(rows2,cols2) if row <col]
    
    ratio = dict()
    for i in np.arange(arr_cor.shape[0]):
        ratio[i] = sum([1 if i in j else 0 for j in correlated_pairs_index])/arr_cor.shape[0]
    # for i,id in enumerate(column_cell_ids):
    #     ratio[id] = sum([1 if i in j else 0 for j in correlated_pairs_index])/len(column_cell_ids)
    return ratio

def compute_correlated_pair_ratio2(arr,column_cell_ids,threshold=0.3):
    """
    compute correlated_pair_ratio for each neuron by shuffle and threshold
    **Significantly correlated pairs of neurons** were defined based on
    the correlation coefficients of Ca2+ transient events within one
    second time bins during context exploration.
    """
    arr_cor = np.corrcoef(arr)
    shuffle_cor = shuffle_corrcoef(arr)
    rows2,cols2 = np.where((arr_cor > np.quantile(shuffle_cor,0.95,axis=0)) & (arr_cor>threshold))
    correlated_pairs_index = [(row,col) for row,col in zip(rows2,cols2) if row <col]
    
    ratio = dict()
    for i,id in enumerate(column_cell_ids):
        ratio[id] = sum([1 if i in j else 0 for j in correlated_pairs_index])/len(column_cell_ids)
    return ratio

def comput_clustering_coefficient_by_session(arr,threshold =0.6):
    """
    compute clustering_coefficient for each neuron


    """
    
    matrix = pd.DataFrame(np.corrcoef(arr),columns=np.arange(0,arr.shape[0]))
    Ng= make_graph(matrix,threshold=threshold )
    _,clustering_coefficient = get_metrics(Ng)
    return clustering_coefficient

def comput_component_probability_by_session(arr,threshold=0.3,comp_size=3):
    """
    arr: coloumns means each observation, raws means firing rate in each timestamps
    threshold: the Pearson's correlation coefficient of two neurons are paired
    
    Explain:
        A connected component is defined as a subgraph of nodes connected to each other by paths but not connected to any other nodes. 
        **Each neuron was assigned either a 0 or 1 indicating whether it was a component member**,
         and the proportion of neurons in a component (component probability) was computed for each imaging session
    """
    
    matrix = pd.DataFrame(np.corrcoef(arr),columns=np.arange(0,arr.shape[0]))
    Ng= make_graph(matrix,threshold=threshold)
    return frac_nodes_in_component(Ng.network,comp_size)


                        




class NeuronNetwork:
    """
    This is a wrapper class for the NetworkX graph data structure. Use this
    class in order to conduct graph theory analysis on networks of neurons
    that were observed during experiments/trials.
    """

    def __init__(self, neurons, connections):
        self.neurons = list(neurons)
        self.connections = connections
        self.network = self.create_graph(self.neurons, self.connections)

    @property
    def comps(self):
        return nx.connected_components(self.network)
    
    def create_graph(self, nodes, edges):
        """Wrapper function for creating a NetworkX graph.

        Each individual column of the provided DataFrame will be represented by
        a single node in the graph. Each pair of correlated nodes (neurons)
        will be connected by an edge, where the edge will receive a weight of
        the specific correlation coefficient of those two nodes.

        Args:
            nodes: list
                A list of all the neurons/nodes in the network/graph.

            edges: dict {(int, int): scalar, ..., (int, int): scalar}
                A dictionary of key-value pairs, where each key is a tuple
                representing an edge between two neurons/nodes, and each value
                is a scalar value representing the weight of that edge.

        Returns:
            graph: NetworkX graph
                A graph of the neuronal network.
        """
        graph = nx.Graph()
        graph.add_nodes_from(nodes)

        for edge in edges:
            graph.add_edge(edge[0], edge[1], weight=edges.get(edge, None))

        return graph

    def plot(self, **kwargs):
        """A wrapper function for plotting a NetworkX graph

        This function will draw a provided NetworkX graph using either the
        spring layout algorithm, or by the positions provided.

        Args:
            pos: dict, optional, default: networkx.drawing.layout.spring_layout
                A dictionary of the network's neurons as keys and their (x, y)
                coordinates as corresponding values.

            node_size: int, optional
                The size of the plotted neurons in the network.

            node_colors: list, optional
                The colors of the neurons to be plotted.

            fontsize: int, optional, default: 10
                The size of the font labelling the plotted neurons.

            draw_edges: bool, optional, default: True
                When True, the edges between all nodes will be drawn. When
                False, the edges between all nodes will be omitted from the
                figure.

            save: bool, optional, default: False
                When True, the plotted figure will be saved to the current
                working directory with its title as the file name, in PDF
                format.

            title: str, optional, default: None
                The title of the plotted graph/network.

            a: float, optional
                The transparency of the nodes
                
            label_nodes: bool, optional
                Whether to display node labels. Default is True
                
            edge_a: float, optional
                The transparency of the edges. Default is 1
            
            edge_weight: float, optional
                The width of the edge. Default is 2
                
            label_edges: bool, optional
                Whether to display edge labels. Default is False.

        Returns:
            pos: dict
                A dictionary of the network's neurons as keys and their (x, y)
                coordinates as corresponding values.
        """

        # Get positions for all nodes
        pos = kwargs.get("pos", None)
        if pos is None:
            print("You did not provide a neuron position dictionary. The spring layout function will be used to plot the network", file=sys.stderr)
            pos = nx.spring_layout(self.network, weight="weight");

        # Size of the plot
        figsize = kwargs.get("figsize", (30, 30))
        plt.figure(figsize=figsize)

        # Nodes
        node_size = kwargs.get("node_size", 600)
        node_colors = kwargs.get("node_colors", self.neurons)
        a = kwargs.get('a',.5)
        disp_node_labels=kwargs.get('label_nodes',True)
        nx.draw_networkx_nodes(self.network, pos, alpha=a, node_size=node_size, cmap=plt.cm.Dark2, node_color=node_colors)

        _, weights = zip(*nx.get_edge_attributes(self.network, "weight").items())

        # Draw edges
        edgeweight=kwargs.get('edgeweight',2)
        edge_a = kwargs.get('edge_a',1)
        edge_color = kwargs.get('edgecolor',weights)
        edge_cmap = kwargs.get('edge_cmap',plt.cm.coolwarm)
        edgelist = kwargs.get('edgelist',self.network.edges)
        if kwargs.get("draw_edges", True):
            nx.draw_networkx_edges(self.network, pos, alpha=edge_a, width=edgeweight,edge_color=edge_color,edge_cmap=edge_cmap,edgelist=edgelist)
            sm = plt.cm.ScalarMappable(cmap=edge_cmap)
            sm._A = []
            #cbar = plt.colorbar(sm, shrink=0.2, aspect=10, anchor = (0,10))
  
        
        # Labels
        
        label_edges=kwargs.get("label_edges",False)
        if label_edges:
            font_size = kwargs.get("font_size", 10)
            nx.draw_networkx_labels(self.network, pos, font_size=font_size)

        if disp_node_labels:
            font_size = kwargs.get("font_size", 10)
            nx.draw_networkx_labels(self.network, pos, font_size=font_size)
        
        title = kwargs.get("title", None)
        plt.title(title)
        plt.axis("off")

        save_to_file = kwargs.get("save", False)
     
        if save_to_file:
            file_name=kwargs.get("file_name","Graph")
            plt.savefig(file_name, dpi=300)

        plt.show()
        return pos
    
    def get_neighbors(self,neurons=None):
        """
        Returns a list of neighbors of a list of nodes
        
        inputs:
        g: graph with which to search for neighbors
        neurons: list of nodes to find neighbors of
        
        outputs:
        neighbors: list of neighbors
        
        """
        
        neighbors = []
        for n in self.neurons:
            if n in neurons:
    
                try:
                    neighbors.extend(list(self.network.neighbors(n)))
                except KeyError:
                    neighbors = list(self.network.neighbors(n))
        neighbors = set(neighbors)
        return neighbors
    
    
    def compute_connection_density(self):
        """Computes the connection density of a network of neurons.

            Connection density is the actual number of edges in the graph as a
            proportion of the total number of possible edges and is the simplest
            estimator of the physical cost — for example, the energy or other
            resource requirements — of a network. (Bullmore et al. 2009)

            Total number of possible edges is: n(n-1)/2,
            where n is the number of nodes (neurons) in the graph.
        """
        num_of_neurons = len(self.neurons)
        possible_num_of_edges = (num_of_neurons * (num_of_neurons-1)) / 2
        return len(list(self.network.edges())) / possible_num_of_edges

    def mean_betw_cent(self, weight="weight"):
        """Computes the mean betweeness centrality of a network of neurons.

            The centrality of a node measures how many of the shortest paths
            between all other nodes pairs in the network pass through it. A node
            with high centrality is thus crucial to efficient communication.
            (Bullmore et. al. 2009)

            https://en.wikipedia.org/wiki/Betweenness_centrality
        """
        betw_centrality = nx.betweenness_centrality(self.network, weight=weight)
        return np.mean(list(betw_centrality.values()))

    def compute_mean_degree_cent(self):
        """Computes the mean degree centrality of a network of neurons.

            The centrality of a node measures how many of the shortest paths
            between all other nodes pairs in the network pass through it. A node
            with high centrality is thus crucial to efficient communication.
            (Bullmore et. al. 2009)

            https://en.wikipedia.org/wiki/Centrality#Degree_centrality
        """
        graph_centrality = nx.degree_centrality(self.network)
        return np.mean(list(graph_centrality.values()))

    def compute_mean_eigen_cent(self):
        """Computes the mean Eigenvector centrality of a network of neurons.

            The centrality of a node measures how many of the shortest paths
            between all other nodes pairs in the network pass through it. A node
            with high centrality is thus crucial to efficient communication.
            (Bullmore et. al. 2009)

            https://en.wikipedia.org/wiki/Eigenvector_centrality
        """
        graph_centrality = nx.eigenvector_centrality(self.network, weight="weight")
        return np.mean(list(graph_centrality.values()))

    def compute_mean_katz_cent(self):
        """Computes the mean Katz centrality of a network of neurons.

           The centrality of a node measures how many of the shortest paths
           between all other nodes pairs in the network pass through it. A node
           with high centrality is thus crucial to efficient communication.
           (Bullmore et. al. 2009)

           https://en.wikipedia.org/wiki/Katz_centrality
        """
        graph_centrality = nx.katz_centrality(self.network, weight="weight")
        return np.mean(list(graph_centrality.values()))

    def compute_mean_load_cent(self):
        """Computes the mean load centrality of a network of neurons.

            The centrality of a node measures how many of the shortest paths
            between all other nodes pairs in the network pass through it. A node
            with high centrality is thus crucial to efficient communication.
            (Bullmore et. al. 2009)
        """
        graph_centrality = nx.load_centrality(self.network, weight="weight")
        return np.mean(list(graph_centrality.values()))

    def compute_max_clique_size(self):
        """Computes the size of the maxiumum clique in the network of neurons.

            A maximum clique of a graph, G, is a clique, such that there is no
            clique with more vertices.

            https://en.wikipedia.org/wiki/Clique_(graph_theory)#Definitions
        """
        return len(clique.max_clique(self.network))

    def compute_mean_clique_size(self):
        """Computes the mean clique size in the network of neurons.

        Finds all cliques in an undirected graph (network), and computes the
        mean size of all those cliques.

        Returns:
            mean: float
                The mean clique size of the network of neurons.
        """
        all_cliques = nx.enumerate_all_cliques(self.network)

        size = 0
        running_sum = 0
        for cliq in all_cliques:
            size += 1
            running_sum += len(cliq)

        mean = running_sum / size
        return mean

    def avg_shortest_path_len(self, weight="weight"):
        """Computes the average path shortest path length.

        This function computes the average path length L, as the average
        length of the shortest path connecting any paid of nodes in a
        network.

        Args:
            weight: str or None, optional, default: None
                If None, every edge has weight/distance/cost 1. If a string, use
                this edge attribute as the edge weight. Any edge attribute not
                present defaults to 1.

        Returns:
            avg_shortest_path_len: float
                The average shortest path length in the network of neurons.

        """
        graph = self.network
        node_list = self.neurons
        shortest_path_lengths = []

        for node_pair in itertools.combinations(node_list, 2):
            source = node_pair[0]
            target = node_pair[1]
            if not nx.has_path(graph, source, target):
                continue

            shortest_path_lengths.append(nx.shortest_path_length(graph, source=source, target=target, weight=weight))

        avg_shortest_path_len = np.mean(shortest_path_lengths)
        return avg_shortest_path_len

    def small_worldness(self, weight="weight"):
        """Computes the small worldness of the neuron network.

        Returns:
            small_worldness: float
                The clustering coefficient divided by the average shortest path
                length of the neuron network.
        """
        cluster_coeff = nx.average_clustering(self.network, weight=weight)
        avg_shortest_path_len = self.avg_shortest_path_len(weight=weight)
        small_worldness = cluster_coeff / avg_shortest_path_len
        return small_worldness

def corrdf_to_dict(dataframe,cutoff):
    """
    dataframe, Pearson's correlation coefficient of each two neurons
    cutoff, larger than which
     the Pearson's correlation coefficient of two neurons are paired
    """
    connections = {}
    
    for neuron_pair in itertools.combinations(dataframe.columns, 2):
               
        corrcoef = dataframe.loc[neuron_pair[0],neuron_pair[1]]
        if corrcoef >= cutoff:
            connections[neuron_pair] = corrcoef
        
    return connections

def make_graph(matrix, threshold):
    connections = corrdf_to_dict(matrix, threshold)
    g = NeuronNetwork(matrix.columns,connections)   
    
    return g

def make_graphs(corr_matrices, threshold):
    """
    corr_matrices,dict.keys are session names, values are session dataframes
    """
    graphs = {}
    for k,v in corr_matrices.items():
        graphs[k] = make_graph(v, threshold)
    return graphs

def get_celltypes(neurons, ctx_shock_cells, ctx_shock_neighbors, name):
    """

    """
    shock_cells = ctx_shock_cells[name]
    shock_neighbors = list(ctx_shock_neighbors[name])
    ns_cells = list(set(neurons) - set(shock_cells) - set(shock_neighbors))
    
    return shock_cells, shock_neighbors, ns_cells

def get_neighbors(g=None,neurons=None):
    """
    Returns a list of neighbors of a list of nodes
    
    inputs:
    g: graph with which to search for neighbors
    neurons: list of nodes to find neighbors of
    
    outputs:
    neighbors: list of neighbors
    
    """
    
    neighbors = []
    for n in g.neurons:
        if n in neurons:

            try:
                neighbors.extend(list(g.network.neighbors(n)))
            except KeyError:
                neighbors = list(g.network.neighbors(n))
    neighbors = set(neighbors)
    return neighbors

def label_list(neuronlist, *sublists, labels=['red','blue'],both="purple"):
    """
    返回一个list 对应neuronlist中的每一个neuron，内含颜色
    returns a list of labels for plotting graphs
    
    inputs: 
        neuronlist: a list of all the neurons
        sublists: 1 or 2 lists of neurons to be labeled  列表中是neurons id
        labels: 2 or 3 labels to apply to the lists, and neurons not in either list (there must be 1 more label then there are lists)
    outputs:
        list of labels corresponding to the neurons in neuronlist    
    """
    
    if (len(labels) -1 != len(sublists)):
        raise ValueError('Please enter 1 more color than sublists')
   
    c_list = []

    if len(sublists)==1:
        
        c1 = labels[0]
        c2 = labels[1]
        s1 = sublists[0]
        
        for i,n in enumerate(neuronlist):
            if n in s1:
                c_list.append(c1)
            else:
                c_list.append(c2) 
        #return c_list 
    
    elif len(sublists)==2:
    
        c1=labels[0]
        c2=labels[1]
        c3=labels[2]
        
        s1 = sublists[0]
        s2 = sublists[1]
        
        for i,n in enumerate(neuronlist):
            if n in s1:
                if n in s2:
                    c_list.append(both)
                else:
                    c_list.append(c1)
            elif n in s2:
                c_list.append(c2) 
            else:
                c_list.append(c3)
            
    return c_list 


    #computations relating to components 

def num_elements_component(comps):
    #input: list of sets (output from nx.connected_components)
    #output: number of nodes in the components
    
    num_nodes = 0
    
    for c in comps:
        num_nodes += len(c)
    
    return num_nodes
    
def frac_nodes_in_component(g,threshold):
    """inputs
            g: graph # or NeuronNetwork.network
            threshold: minimum size of component
            
        output
            fraction of nodes that are in a connected component larger than threshold
    """
    comps = list(nx.connected_components(g))
    big_comps = [c for c in comps if len(c) > threshold]
    #print(sorted(big_comps, key=len))
    num_nodes = num_elements_component(big_comps)
    
    return num_nodes / len(g)
    
    
def is_component_member(g,neuron,threshold):
    """
    inputs
        g: graph
        neuron: name of cell to test whether its in component
        threshold: minimum component size
    output:
        0 if node is not in a component, 1 if node is in component
    
    """
    comps = list(nx.connected_components(g))
    big_comps = [c for c in comps if len(c) > threshold]
    #print(big_comps)
    for c in big_comps:
        if neuron in c: return 1
    return 0

def is_shock_component_member(g,neuron,threshold,shock_cells):
    """
    inputs
        g: graph
        neuron: name of cell to test whether its in a shock cell-containing component
        threshold: minimun component size
        shock_cells: list of cells that must be found in a component
    
    output
        0 if node is not in a shock-containing component, 1 if node is in component
    """
    comps = list(nx.connected_components(g))
    big_comps = [c for c in comps if len(c) > threshold]
    shock_comps = [c for c in big_comps if (not c.isdisjoint(shock_cells))]
    #print(big_comps)
    for c in shock_comps:
        if neuron in c: return 1
    return 0

#helper methods to get graph metrics
def get_metrics(g):
    # Get metrics for one graph，containing degree_cent and uw_cc

    
    #degree centrality (unweighted degree- requires thresholding)
    dc = list(nx.degree_centrality(g.network).values())
    degree_cent = pd.Series(data=nx.degree_centrality(g.network))

    #unweighted clustering coefficient
    uw_cc = pd.Series(data=nx.clustering(g.network))
    
    return degree_cent, uw_cc

def graph_metrics_simple(graphs):
    metrics = pd.DataFrame()
    for k,v in graphs.items():
        dc,cc = get_metrics(v)
        df = pd.DataFrame(data={'Degree_Centrality': dc, 'Unweighted_CC':cc, 'Day':k})
        df.index.name='Neuron'
        metrics = pd.concat([metrics,df])
    return metrics.reset_index()