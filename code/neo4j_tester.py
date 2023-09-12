from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

class Neo4jConnectionTester:
    def __init__(self):
        load_dotenv()
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def test_connection(self):
        with self.driver.session() as session:
            greeting = session.run("RETURN 'Hello, World!' as greeting").single().value()
            return greeting

if __name__ == "__main__":
    tester = Neo4jConnectionTester()
    print(tester.test_connection())
    tester.close()