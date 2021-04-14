"""
Test GraphQL endpoint
"""
import pytest
from graphene import Schema
from graphene.test import Client
from forest_lite.server.routers.graphql import Query


@pytest.fixture
def client():
    schema = Schema(query=Query)
    return Client(schema)


def test_schema_colorbrewer_by_kind(client):
    response = client.execute('''
        {
            colorbrewer(kind: SEQUENTIAL) {
                name
            }
        }
    ''')
    actual = [item["name"] for item in response["data"]["colorbrewer"]]
    assert actual == [ "Blues", "Reds" ]


def test_schema_colorbrewer_by_kind_and_level(client):
    """Example using variables with GraphQL query syntax"""
    response = client.execute('''
        query Query($level: Int) {
            colorbrewer(kind: SEQUENTIAL, level: $level) {
                name
            }
        }
    ''', variables={ "level": 5 })
    actual = [item["name"] for item in response["data"]["colorbrewer"]]
    assert actual == [ "Blues" ]
