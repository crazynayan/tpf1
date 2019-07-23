import networkx as nx
from networkx import DiGraph
from models import State


class Analyze:
    def __init__(self, nodes, root=None):
        if root is None:
            self.root_label = next((label for label in nodes.keys() if label[:2] == '$$'), None)
        else:
            self.root_label = root
        graph = DiGraph()
        # Add all the goes and falls edges
        for label, node in nodes.items():
            graph.add_node(label)
            for next_label in node.get_next():
                graph.add_edge(label, next_label)
        # Add returns to nodes
        call_nodes = [node for _, node in nodes.items() if node.get_call()]
        return_nodes = [node for _, node in nodes.items() if node.is_return]
        for call_node in call_nodes:
            return_node = next(return_node for return_node in return_nodes
                               if nx.has_path(graph, call_node.get_call(), return_node.label))
            call_node.set_return(return_node.label)
            return_node.set_return(call_node.fall_down)
        # Add goes edges to subroutine calls
        for call_node in call_nodes:
            graph.add_edge(call_node.label, call_node.get_call())
            return_node = nodes[next(iter(call_node.get_returns()))]
            if len(return_node.get_returns()) == 1:
                # Include subroutine to the main path if there is only one call
                graph.add_edge(return_node.label, call_node.fall_down)
                graph.remove_edge(call_node.label, call_node.fall_down)
        # Create a DAG (Directed Acyclic Graph) from the graph. (Remove cycles)
        dag = graph.copy()
        loop_edges = list()
        while not nx.is_directed_acyclic_graph(dag):
            cycle_edges = nx.find_cycle(dag, self.root_label)
            loop_edges.append(cycle_edges[-1])
            dag.remove_edge(*cycle_edges[-1])
        # Add loops to the nodes
        for loop_edge in loop_edges:
            nodes[loop_edge[0]].set_loop(loop_edge[1])
        # Reduce all the extra paths ('OR' paths) in the dag
        dag = nx.transitive_reduction(dag)
        # Save paths to all exit points
        exit_labels = [node.label for _, node in nodes.items() if node.is_program_exit]
        flows = dict()
        for exit_label in exit_labels:
            paths = list(nx.all_simple_paths(dag, self.root_label, exit_label))
            flows[exit_label] = [{'path': path} for path in paths]
        # Save graphs, nodes and paths
        self.dag = dag
        self.graph = graph
        self.nodes = nodes
        self.flows = flows

    def show(self, exit_label):
        for flow in self.flows[exit_label]:
            state = State(flow['path'])
            state.capture_set = True
            for label in flow['path']:
                state.label = label
                for component in self.nodes[label].components.list_values:
                    state = component.execute(state)
            flow['state'] = state
        # Print to Terminal
        print(f"{'*'*60} VALID PATH {'*'*60}")
        valid_flows = [flow for flow in self.flows[exit_label] if flow['state'].valid]
        for index, flow in enumerate(valid_flows):
            print(index+1, flow['path'])
        for index, flow in enumerate(valid_flows):
            print(index+1, flow['state'].condition)
        print(f"{'*'*59} INVALID PATH {'*'*59}")
        invalid_flows = [flow for flow in self.flows[exit_label] if not flow['state'].valid]
        for index, flow in enumerate(invalid_flows):
            print(index+1, flow['path'])
        for index, flow in enumerate(invalid_flows):
            print(index+1, flow['state'].condition)
        for index, flow in enumerate(valid_flows):
            print(f"{'*'*60} VALID {index+1:4} {'*'*60}")
            print('\n'.join(flow['state'].text))
            print(f"Required {flow['state'].condition}")
            print(f"Output   {flow['state'].known}")
        for index, flow in enumerate(invalid_flows):
            print(f"{'*'*60} INVLD {index+1:4} {'*'*60}")
            print('\n'.join(flow['state'].text))
