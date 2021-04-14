"""
Test GraphQL endpoint
"""
from graphene import Schema
from forest_lite.server.routers.graphql import Query



def test_schema():
    schema = Schema(query=Query)
    response = schema.execute('''
        { hello(name: "Bob") }
    ''')
    assert response.data == {"hello": "Hello, Bob!"}
