"""GraphQL endpoint"""
from fastapi import APIRouter
from starlette.graphql import GraphQLApp
import graphene
from graphene import Field, List, String, Int


class Kind(graphene.Enum):
    SEQUENTIAL = 0
    DIVERGING = 1
    CATEGORICAL = 2


class Palette(graphene.ObjectType):
    name = String()
    kind = Kind()
    levels = List(Int)


class Query(graphene.ObjectType):
    colorbrewer = Field(List(Palette), kind=Kind())

    def resolve_colorbrewer(root, info, kind=None):
        # TODO: Parse colorbrewer.json into a list of Palette types
        palettes = [
            Palette(name="Reds", kind=Kind.SEQUENTIAL, levels=[3, 5, 6]),
            Palette(name="Set3", kind=Kind.CATEGORICAL, levels=[3, 4, 5, 6, 7, 8])
        ]
        if kind is None:
            return palettes
        else:
            return [palette for palette in palettes
                    if palette.kind == kind]


router = APIRouter()


router.add_route("/graphql", GraphQLApp(schema=graphene.Schema(query=Query)))
