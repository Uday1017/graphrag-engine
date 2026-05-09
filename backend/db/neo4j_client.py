from neo4j import GraphDatabase
from utils.config import settings

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password)
        )
    return _driver

def run_query(cypher: str, params: dict = {}) -> list[dict]:
    driver = get_driver()
    with driver.session() as session:
        result = session.run(cypher, params)
        return [dict(record) for record in result]

def create_paper_node(paper: dict):
    run_query(
        """
        MERGE (p:Paper {id: $id})
        SET p.title = $title,
            p.abstract = $abstract,
            p.year = $year,
            p.url = $url
        """,
        paper
    )

def create_author_and_link(author_name: str, paper_id: str):
    run_query(
        """
        MERGE (a:Author {name: $name})
        WITH a
        MATCH (p:Paper {id: $paper_id})
        MERGE (a)-[:WROTE]->(p)
        """,
        {"name": author_name, "paper_id": paper_id}
    )

def create_topic_and_link(topic: str, paper_id: str):
    run_query(
        """
        MERGE (t:Topic {name: $topic})
        WITH t
        MATCH (p:Paper {id: $paper_id})
        MERGE (p)-[:BELONGS_TO]->(t)
        """,
        {"topic": topic, "paper_id": paper_id}
    )

def close():
    if _driver:
        _driver.close()
