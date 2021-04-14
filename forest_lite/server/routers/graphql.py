"""GraphQL endpoint"""
from fastapi import APIRouter
from starlette.graphql import GraphQLApp
import graphene


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="World!"))
    colorbrewer = graphene.String()

    def resolve_hello(root, info, name):
        return "Hello, " + name + "!"

    def resolve_colorbrewer(root, info):
        return "Colorbrewer"


router = APIRouter()


router.add_route("/graphql", GraphQLApp(schema=graphene.Schema(query=Query)))
