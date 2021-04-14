"""GraphQL endpoint"""
from fastapi import APIRouter
from starlette.graphql import GraphQLApp
import graphene


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="World!"))

    def resolve_hello(self, info, name):
        return "Hello, " + name + "!"


router = APIRouter()


router.add_route("/graphql", GraphQLApp(schema=graphene.Schema(query=Query)))
