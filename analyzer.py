import ast
import pkgutil
import importlib
import inspect
import sys
import plugins
vprint = print if ("-v" in sys.argv[1:]) else lambda *a, **k: None

def load_plugins():
    """Returns a list of objects that implement the Base plugin interface."""
    Plugins = []
    # Loading python modules from plugins folder
    Modules = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules(plugins.__path__, plugins.__name__ + ".")
    }

    for plugin_name in Modules.keys():
        # Checking every class in the module
        for name, cls in inspect.getmembers(Modules[plugin_name], inspect.isclass):
            if issubclass(cls, plugins.Base.TransformerBase):
                Plugins.append(cls())
                print(f"PLUGIN: {name} succesfully loaded!")
    return Plugins

class Analyzer(ast.NodeVisitor):
    def __init__(self, transformers):
        self.transformers = transformers
        self.results = {}

    def visit_If(self, node):
        vprint(f"ANALYZER: Found and If, at line number: {node.lineno}")
        for transformer in self.transformers:
            if transformer.visit(node):
                if(node not in self.results.keys()):
                    self.results[node] = [transformer]
                else:
                    self.results[node].append(transformer)
        

def main():
    with open("test.py", "r") as src:
        tree = ast.parse(src.read())    

    analyzer = Analyzer(load_plugins())    
    analyzer.visit(tree)
    with open("transformed.py", "w") as out:
        for node in analyzer.results.keys():
            for transformer in analyzer.results[node]:
                print(f"If node at line number [{node.lineno}] can be transformed with plugin: [{transformer.__class__.__name__}]")
                out.write("#"+"-"*10 + str(node.lineno) + "-"*10 + f"[{transformer.__class__.__name__}]"+"\n")
                out.write(ast.unparse(transformer.transform(node)) + "\n")
                out.write("#"+"-"*9 +"/"+ str(node.lineno) + "-"*10 + "\n")
        

if __name__ == "__main__":

    main()
    vprint("Done")

    
