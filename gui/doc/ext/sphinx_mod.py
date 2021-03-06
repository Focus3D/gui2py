import sys
import os
import inspect


# Events
from sphinx.ext.autodoc import MethodDocumenter, ModuleDocumenter

class EventDocumenter(MethodDocumenter):
    objtype = "event"
    member_order = 45
    priority = 5

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        if member.__doc__ is not None:
            if ":event:" in member.__doc__:
                return inspect.isroutine(member) and \
                       not isinstance(parent, ModuleDocumenter)  
        return False
          
def setup(app):
    app.add_autodocumenter(EventDocumenter)



# Search all submodules
def find_modules(rootpath, skip):
    """
    Look for every file in the directory tree and return a dict
    Hacked from sphinx.autodoc
    """

    INITPY = '__init__.py'

    rootpath = os.path.normpath(os.path.abspath(rootpath))
    if INITPY in os.listdir(rootpath):
        root_package = rootpath.split(os.path.sep)[-1]
        print "Searching modules in", rootpath
    else:
        print "No modules in", rootpath
        return

    def makename(package, module):
        """Join package and module with a dot."""
        if package:
            name = package
            if module:
                name += '.' + module
        else:
            name = module
        return name

    skipall = []
    for m in skip.keys():
        if skip[m] is None: skipall.append(m)

    

    tree = {}
    saved = 0
    found = 0
    def save(module, submodule):
        name = module+ "."+ submodule
        
        for s in skipall:
            if name.startswith(s):
                print "Skipping "+name
                return False
        if skip.has_key(module):
            if submodule in skip[module]:
                print "Skipping "+name
                return False
        if not tree.has_key(module):
            tree[module] = []
        tree[module].append(submodule)
        return True
                    
    for root, subs, files in os.walk(rootpath):
        py_files = sorted([f for f in files if os.path.splitext(f)[1] == '.py'])
                    
        if INITPY in py_files:
            subpackage = root[len(rootpath):].lstrip(os.path.sep).\
                replace(os.path.sep, '.')
            full = makename(root_package, subpackage)
            part = full.rpartition('.')
            base_package, submodule = part[0], part[2]
            found += 1
            if save(base_package, submodule): saved += 1
            
            py_files.remove(INITPY)    
            for py_file in py_files:
                found += 1
                module = os.path.splitext(py_file)[0]
                if save(full, module): saved += 1
    for item in tree.keys():
        tree[item].sort()
    print "%s contains %i submodules, %i skipped" % \
          (root_package, found, found-saved)

    return tree

