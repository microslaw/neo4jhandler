from neo4j import GraphDatabase
import os
from pyvis.network import Network
import hidden
import networkx as nx
import webbrowser

# e.g. hidden.py:
#
# uri="neo4j://localhost"
# user="neo4j"
# password="password"


class NodeType:
    def __init__(self, node):
        self.id = int(node.element_id.split(":")[-1])
        self.properties = {}
        self.labels = set(node.labels)

        for key in node.keys():
            self.properties[key] = node.get(key)

    def to_JSON(self):
        return {
            "id": self.id,
            "properties": self.properties,
            "labels": list(self.labels),
        }


class RelationType:
    def __init__(self, record):
        left, right = record[0].nodes
        self.nodes = NodeType(left), NodeType(right)

        # !!! might not be unique, look into later
        self.id = record[0].element_id
        self.type = record[0].type
        self.properties = {}

        for key in record[0].keys():
            self.properties[key] = record[0].get(key)

    def to_JSON(self):
        return {
            "id": self.id,
            "nodes": [node.to_JSON() for node in self.nodes],
            "type": self.type,
            "properties": self.properties,
        }


def check_connection() -> None:
    try:
        with GraphDatabase.driver(
            hidden.uri, auth=(hidden.username, hidden.password)
        ) as driver:
            driver.verify_connectivity()
        print("Connected")
    except Exception as e:
        print("Connection failed. Verify credits in hidden.py")
        exit(1)


def execute_query(query: str, database: str = "neo4j") -> tuple:
    with GraphDatabase.driver(
        hidden.uri, auth=(hidden.username, hidden.password), database=database
    ) as driver:
        records, summary, keys = driver.execute_query(query)

        return records, summary, keys


def relations_to_graph(relations: list[RelationType]) -> nx.MultiDiGraph:

    G = nx.MultiDiGraph()

    for relation in relations:
        left, right = relation.nodes

        G.add_node(left.id, data=left.to_JSON())
        G.add_node(right.id, data=right.to_JSON())
        G.add_edge(left.id, right.id, data=relation.to_JSON())


    return G


def display_graph(G: nx.Graph):

    nt = Network(height="1000", width="100%")
    nt.from_nx(G)

    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    nt.save_graph("tmp/nx.html")
    url = f"file:///{os.getcwd()}/tmp/nx.html"
    webbrowser.open(url, new=0, autoraise=True)


def load_query(filename: str) -> str:
    with open(f"queries/{filename}.cypher", "r") as rfile:
        return rfile.read()


check_connection()
while True:
    filename = input("Enter query file name: ")
    query = load_query(filename)
    records, summary, keys = execute_query(query)
    relations = [RelationType(relation) for relation in records]
    G = relations_to_graph(relations)
    display_graph(G)
