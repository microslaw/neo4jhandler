from neo4j import GraphDatabase

import hidden

# e.g. hidden.py:
#
# uri="neo4j://localhost"
# user="neo4j"
# password="password"


def check_connection():
    try:
        with GraphDatabase.driver(
            hidden.uri, auth=(hidden.username, hidden.password)
        ) as driver:
            driver.verify_connectivity()
        print("Connected")
    except Exception as e:
        print("Connection failed. Verify credits in hidden.py")
        exit(1)


def execute_query(query, database="neo4j"):
    with GraphDatabase.driver(
        hidden.uri, auth=(hidden.username, hidden.password)
    ) as driver:
        with driver.session(database=database) as session:
            result = session.run(query)
            return result


check_connection()
with open("queries/test.cypher", "r") as f:
    query = f.read()

result = execute_query(query)
print(result)
