from nanopub.trustyuri.file.FileModule import FileModule
from nanopub.trustyuri.rdf.RdfModule import RdfModule

modules: dict = {}


def add_module(module):
    modules[module.module_id()] = module


def get_module(name):
    return modules[name]


add_module(FileModule())
add_module(RdfModule())
