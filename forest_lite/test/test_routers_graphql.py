"""
Test GraphQL endpoint
"""
from collections import OrderedDict
from graphene import Schema
from graphene.test import Client
from forest_lite.server.routers.graphql import Query



def test_schema_colorbrewer():
    schema = Schema(query=Query)
    client = Client(schema)
    response = client.execute('''
        {
            colorbrewer(kind: SEQUENTIAL) {
                name
            }
        }
    ''')
    assert response["data"]["colorbrewer"] == [
            OrderedDict([
                ("name", "Reds")
            ])
        ]
