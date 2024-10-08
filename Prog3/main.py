"""Main file for spawning processes and running experiments"""
import os
import sys
import time
from node import Node
from modules.utils import Edge, EdgeStatus
from modules.kruskals import Kruskals
from multiprocessing import Process, Queue, Value, Array

def print_output(raw_edges, mst):
    """Print the tree edges into the output file
    
    Arguments:
        raw_edges {List} -- List of all edges
        mst {List} -- List of indexes of the tree edges
    
    Returns:
        Float -- Sum of weights of all the tree edges
    """
    tree_edges = []
    tree_weight = 0
    for _in in range(len(mst)):
        in_mst = mst[_in]
        if in_mst:
            tree_edges.append(raw_edges[_in])

    # Sort the tree edges according to their weights
    tree_edges.sort(key=lambda x: float(x[2]))
    for edge in tree_edges:
        node1 = int(edge[0])
        node2 = int(edge[1])
        tree_weight += float(edge[2])
        if node1 < node2:
            print('(' + str(node1) + ', ' + str(node2) + ', ' +
                  str(edge[2].strip()) + ')')
        else:
            print('(' + str(node2) + ', ' + str(node1) + ', ' +
                  str(edge[2].strip()) + ')')

    # Return the weight of the tree generated by the GHS Algorithm
    return tree_weight


def spawn_process(node_id, name, msg_q, wake_count, total_messages, mst):
    """Spawn a new process for node with given name and adjacent edges
    
    Arguments:
        node_id {Integer} -- Node Id
        name {Float} -- Fragment Name, initially zero for all
        msg_q {Multiprocessing Queue} -- Queue for the node
        wake_count {Multiprocessing Value} -- Shared value of wake count
        total_messages {Multiprocessing Value} -- Shared total messages value
        mst {Multiprocessing Array} -- List of edge indexes
    
    Returns:
        Bool -- Whether the MST was completed or not
    """
    global wake_processes, debug_level, edges
    node = Node(node_id, edges[node_id], name, msg_q, debug_level)

    # Wake up certain processes.
    # print(wake_count.value)
    with wake_count.get_lock():
        if wake_count.value < wake_processes:
            wake_count.value += 1
            node.wakeup()

    node_messages = node.start_operation()
    with total_messages.get_lock():
        total_messages.value += node_messages

    for edge in edges[node_id]:
        if edge.get_status() == EdgeStatus.branch:
            edge_id = edge.get_id()
            # Check and update mst in a critical section
            with mst.get_lock():
                if not mst[edge_id]:
                    mst[edge_id] = True

if __name__ == '__main__':

    if len(sys.argv) != 4:
        print('To run the file: python main.py <no-of-processes-to-wake-up> ' +
          '<debug-level (basic/info/debug)> <path-to-input-file>')
        sys.exit()

    wake_processes = int(sys.argv[1])
    debug_level = sys.argv[2]
    input_file = sys.argv[3]

    # Read from the input file
    with open(input_file) as file:
        contents = file.readlines()
    contents = [x.strip() for x in contents]

    num_nodes = int(contents[0])
    raw_edges = []
    for line in contents[1:]:
        if len(line) > 1:
            line = line[1:-1].split(',')
            raw_edges.append(line)
        else:
            break

    # Check if wake processes is more than 10% of nodes or not
    if wake_processes < num_nodes // 10:
        # print(
        #     '[WARN]: Number of awake nodes is less than 10% of the total nodes.\n'
        #     + '[INFO]: Raising number of awake processes to 10%')
        wake_processes = num_nodes // 10

    # Attach a queue for each process
    queues = []
    for _ in range(num_nodes):
        q = Queue()
        queues.append(q)

    # Form edges for each node from the given input
    edges = []
    for _ in range(num_nodes):
        edges.append([])

    edge_id = 0
    for raw_edge in raw_edges:
        node1 = int(raw_edge[0])
        node2 = int(raw_edge[1])
        # Same edge_id for both edges between node1 and node2
        edge1 = Edge(edge_id, node1, node2, float(raw_edge[2]), queues[node2])
        edge2 = Edge(edge_id, node1, node2, float(raw_edge[2]), queues[node1])
        edges[node1].append(edge1)
        edges[node2].append(edge2)
        edge_id += 1

    # Spawn processes for each node
    wake_count = Value('i', 0)
    total_messages = Value('i', 0)
    mst = Array('b', [False] * (edge_id + 1))
    processes = []

    start_time = time.time() # Start the timer

    for node_id in range(num_nodes):
        p = Process(target=spawn_process,
                    args=(node_id, 0, queues[node_id], wake_count, total_messages,
                        mst))
        processes.append(p)
        p.start()

    # Join processes before checking the output
    for p in processes:
        p.join()

    mst = list(mst)
    assert mst.count(1) == num_nodes - 1

    end_time = time.time() # End the timer
    total_time = end_time - start_time # Get the processing time of the algorithm

    # Check weight with the tree from kruskals algorithm as well
    weight = print_output(raw_edges, mst)
    k = Kruskals(num_nodes)
    k_weight = k.get_mst(raw_edges)

    assert weight == k_weight, '[CHECK]: Weights from Kruskals and GHS do not match'
    print('[SUCCESS]: Completed Execution. MST Weight: ' + str(weight))

    # Write to file for plotting graph
    script_dir = sys.path[0]
    results_dir = script_dir + '/files'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    with open(results_dir + '/results.txt', 'a') as f:
        f.write(f"{input_file}, {total_messages.value}, {num_nodes}, {len(raw_edges)}, {total_time:.5f}\n")
