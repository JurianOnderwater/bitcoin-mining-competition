# utils/view.py
from server import DIFFICULTY

import networkx as nx
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import matplotlib.patches as mpatches
from datetime import datetime

class Colors:
    """
    shortcuts for printed color in the console.
    """

    def __init__(self):
        pass

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def visualize_tree(node, graph):
    """
    it visualizes a Merkle Tree using graphviz libraries
    :param node:
    :param graph:
    :return:
    """
    if 'data' in node:
        graph.node(node['hash'], label=node['data'])
    else:
        graph.node(node['hash'], label=node['hash'][:8])
        visualize_tree(node['left'], graph)
        graph.edge(node['hash'], node['left']['hash'])
        if 'right' in node:
            visualize_tree(node['right'], graph)
            graph.edge(node['hash'], node['right']['hash'])

def create_visualization_table(fields, row_list, title):
    """

    :param fields: list of fields of the table
    :param row_list: list of every row
    :param title : table title
    :return: PrettyTable object
    """
    table = PrettyTable()

    # Define the column fields
    table.field_names = fields

    # Add rows
    for r in row_list:
        table.add_row(r)

    # add title
    table.title = title
    return table

def visualize_blockchain_terminal(blocks, n_blocks=15):
    """
    Visualize the last ten blocks of the blockchain with different node colors based on their properties.

    :param blocks: A list of Block objects.
    :param n_blocks: number of blocks to be represented
    """
    # Create a new table
    table = PrettyTable()
    table.field_names = ["Block", "Prev Hash", "Nonce", "Time", "Creation Time (s)", "Mined By", "Difficulty"]

    # Add the last ten blocks to the table
    last_ten_blocks = blocks[-n_blocks:]
    for b in last_ten_blocks:
        timestamp = datetime.fromtimestamp(b.time)
        # Format the datetime object as dd-mm-yy : hh:mm:ss
        formatted_time = timestamp.strftime('%d-%m-%y : %H:%M:%S')
        node_color = '\033[91m'  # Red
        if b.main_chain:
            node_color = '\033[94m'  # Light blue
            if b.confirmed:
                node_color = '\033[92m'  # Green
        reset_color = '\033[0m'
        table.add_row([node_color + str(get_hash_for_visualization(b.hash)) + reset_color,
                       node_color + str(get_hash_for_visualization(b.prev)) + reset_color,
                       node_color + str(b.nonce) + reset_color,
                       node_color + formatted_time + reset_color,
                       node_color + str(b.creation_time) + reset_color,
                       node_color + b.mined_by + reset_color,
                       node_color + str(get_difficulty_from_hash(b.hash)) + reset_color])

    # Print the table
    print(table)



def get_difficulty_from_hash(hash):
    """

    :param hash:
    :return:
    """
    diff = 0
    for char in hash:
        if char == '0':
            diff += 1
        else:
            break
    return diff

def visualize_blockchain(blocks, path="vis/blockchain/blockchain.pdf", n_blocks=15):
    """
    Visualize the last ten blocks of the blockchain with different node colors based on their properties.

    :param blocks: A list of Block objects.
    :param path: The path to save the visualization.
    :param n_blocks: number of blocks to be represented
    """
    # Create a new graph
    g = nx.DiGraph()

    # Add the last ten blocks to the graph
    last_ten_blocks = blocks[-n_blocks:]
    for b in last_ten_blocks:
        node_color = 'red'
        if b.main_chain:
            node_color = 'lightblue'
            if b.confirmed:
                node_color = 'green'
        g.add_node(b.hash, color=node_color, label=b.mined_by)

    # Add edges between blocks
    for b in last_ten_blocks:
        if b.prev is not None and b.prev in g:
            g.add_edge(b.hash, b.prev)

    # Draw the graph
    pos = nx.spring_layout(g)
    node_colors = [g.nodes[n]['color'] for n in g.nodes]
    nx.draw(g, pos, node_color=node_colors, labels=nx.get_node_attributes(g, 'label'), with_labels=True)

    # Add color legend
    red_patch = mpatches.Patch(color='red', label='Not on main chain')
    blue_patch = mpatches.Patch(color='lightblue', label='On main chain')
    green_patch = mpatches.Patch(color='green', label='Confirmed')
    plt.legend(handles=[red_patch, blue_patch, green_patch], loc='upper left')

    plt.savefig(path)
    print(Colors.BOLD + "blockchain saved " + Colors.ENDC + "in : " + Colors.OKGREEN + f"{path}" + Colors.ENDC)

def get_hash_for_visualization(hash, n=6):
    """
    it gets the first n-non-zero characters of a block hash. For visualization purpose only.
    :param hash:
    :param n:
    :return:
    """
    hash_str = str(hash)
    non_zero_str = hash_str[DIFFICULTY:]
    first_n_non_zero_chars = non_zero_str.lstrip('0')[:n]
    return first_n_non_zero_chars

def checks_visualizations(text_list, check_list):
    """
    visualize checks for block proposal
    :param text_list: list of text
    :param check_list: list of bool variables
    :return: string to print
    """
    return_message = ""
    for text, check in zip(text_list, check_list):
        if check:
            color_check = Colors.OKGREEN
        else:
            color_check = Colors.FAIL

        return_message += Colors.BOLD + text + Colors.ENDC + ": " + color_check + str(check) + Colors.ENDC + "\n"
    return return_message