import re
from itertools import dropwhile, takewhile
from yaml import load, dump, CLoader as Loader, CDumper as Dumper
import numpy as np
import h5py

def grab_array(line, drop, take):
    
    left = dropwhile(lambda line: drop in line, f)
    chunk = takewhile(lambda line: not re.search('^\n',line), left)
    
    array = []
    
    for line in chunk:
        array += line.split()
    
    array = [float(x) for x in array]
        
    return [array]

keyword_dict = {'KEYWORD1': (1, 
                             lambda l: l.split()[1:], 
                             ('kw1str',), 
                             (str,),
                             ('keyval1',),
                            ),
                'MULTIKEYW': (3,
                              lambda l: l.split()[1:],
                              ('mulstr', 'mulfl', 'mulint'), 
                              (str, float, int),
                              ('mulstr1', 0.0, 0),
                             ),
                'ARRAY': (1,
                          lambda l: grab_array(l, 'ARRAY', ''),
                          ('mularr',),
                          (np.array,),
                          ([1.0, 1.0]),
                         ),
               }

class Keyword:

    def __init__(self,
                 line,
                 parameter,
                 func,
                 attr_name,
                 verification,
                 default):
        
        output = func(line)
        
        for item, attr, ver in zip(output, attr_name, verification):
            try:
                setattr(self, attr, ver(item))
            except:
                setattr(self, attr, str(item))
                
        if len(vars(self)) != parameter:
            for i in range(len(vars(self)),parameter):
                setattr(self, attr_name[i], default[i])
        
        return None
    
    def __getitem__(self, key):
        return getattr(self, key)
    

class Deck:
    
    def __setitem__(self, key, val):
        setattr(self, key, val)
        
        return None
        
    def __getitem__(self, key):
        return getattr(self, key)
    
    def todict(self):
        output_dict = {}
        for var in vars(self):
            output_dict[var] = {}
            for subvar in vars(getattr(self, var)):
                output_dict[var][subvar] = self[var][subvar]

        return output_dict
    
    def toinput(self):
        
        input_string = ''
        for var in vars(self):
            input_string += (f'{var:<12s}    ')
            for subvar in vars(getattr(self, var)):
                input_string += (f'{str(self[var][subvar]):>16s}')
            input_string += '\n'
        
        return input_string

with open('test/test_input.ip', 'r') as f:
    deck = Deck()
    for line in f:
        kw = line.split()[0].upper()
        deck[kw] = Keyword(line, *keyword_dict[kw])

data_dict = deck.todict()

data = dump(deck.todict(), Dumper=Dumper, default_flow_style=False)
yamldict = load(data, Loader=Loader)

with h5py.File('testfile.hdf5', 'w') as h:
    for key in data_dict.keys():
        grp = h.create_group(key)
        if type(data_dict[key]) == dict:
            for subkey in data_dict[key].keys():
                if type(data_dict[key][subkey]) != dict:
                    dset = grp.create_dataset(subkey, data=data_dict[key][subkey])
                    
with h5py.File('testfile.hdf5', 'r') as h:
    h_string = ''
    for key in h.keys():
        h_string += (f'{key:<12s}    ')
        for subkey in h[key].keys():
            path = f'{key}/{subkey}'
            h_string += (f'{str(h[path].value):>16s}')
        h_string += '\n'