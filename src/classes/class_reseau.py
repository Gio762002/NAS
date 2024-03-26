'''
The goal of having all these attributes that seem redundant is to have easier access to information needed for the config.
More importantly, Python is an interpreted language, the main program would had difficulty to create new variables during the execution 
and put aside the function that waits for the information that haven't come yet.
That would went against our design : we want that the main program reads the intent file line by line, and generate configs along the way
as a human would do. A man keeps in mind the information he needs, and the program keeps them in attributes.
'''

class router:
   
    def __init__(self,name,type,private_network=None):
        self.name = name
        self.router_id = None #1.1.1.1
        self.loopback = None
        self.private_network = private_network
        self.all_interfaces = {"Loopback0":1} #interface.name : occupied? (1 or 0)
        self.interfaces = {} #interface.name: interface (instance)
        self.neighbors = [] #router_id, extrait de self.interface
        self.type = type # PE, P, company name
        self.position = None # name of the AS where the router is located, to be tracked for any modification 

    def get_router_id(self):
        self.router_id = ((self.name[1:]+".")*4)[:-1]
    def get_loopback(self):
        self.loopback = self.router_id

class interface:
    
    def __init__(self,name):
        self.name = name # !!! can be the same with other interfaces of other routers
        self.statu = "down" # up or down
        self.address_ipv4 = None
        self.connected_router = None # router_id
        self.connected_interface = None # interface.name
        self.egp_protocol_type = None

class autonomous_system:

    def __init__(self, as_id):
        self.as_id = as_id
        self.routers = {} # router_id : router (instance)
        self.link_dict = {} #(router_id,interface.name):(router_id,interface.name)
        self.loopback_plan = {} # router_id : loopback
        self.egp = "BGP"

    def generate_loopback_plan(self):
        for router_id,router in self.routers.items():
            self.loopback_plan[router_id] = router.loopback

    def eliminate_repeat_link(self):
        link_dict_copy = self.link_dict.copy()
        for ((r1, i1),(r2, i2)) in self.link_dict.items(): #all are strings
            if (r2, i2) in self.link_dict.keys() and (r1, i1) in link_dict_copy.keys():
                del link_dict_copy[(r2, i2)] # eliminate the reverse link to avoid duplicate
        self.link_dict = link_dict_copy

    def update_link_dict(self, r1, r2):
        """delete a link from the link_dict, not used"""
        link_dict_copy = self.link_dict.copy()
        for (rt1,int1),(rt2,int2) in link_dict_copy.items():
            if rt1 == r1 and rt2 == r2:
                del self.link_dict[(rt1,int1)]
                del self.link_dict[(rt2,int2)]

    