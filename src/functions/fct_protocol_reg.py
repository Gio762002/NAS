"""
reg is an instance of the class 'registrar'. 
It is used to store the configuration commands of routers and interfaces properly in the right position 
whatever the order of calls of the functions. 
"""


                            

def as_enable_ospf(As,reg):
    """Implement OSPF for all routers in the As"""
    process_id = 100
    order = 1 # TODO check if it is the right order
    for router in As.routers.values():
        reg.write(router.name, order, "router ospf " + str(process_id))
        reg.write(router.name, order, " router-id " + router.router_id)
        reg.write(router.name, order, " log-adjacency-changes")
        reg.write(router.name, order, " network " + str(router.loopback) + "0.0.0.0 area 0")
        for interface in router.interfaces.values():
            if interface.statu == "up" and interface.egp_protocol_type != "eBGP":
                reg.write(router.name, order, " network " + str(interface.address_ipv4) + "0.0.0.3 area 0")
#  router ospf 100
#  router-id 1.1.1.1
#  log-adjacency-changes
#  network 1.1.1.1 0.0.0.0 area 0
#  network 10.0.0.1 0.0.0.0 area 0
# !

         
# def generate_eBGP_neighbor_info(dict_as):
#     '''
#     For all ABR in all as, mark their ebgp interface and find the info of its connected int.
#     RETURN: {(as,router,ABR_interface,@int,community):(as,router_id,ABR_interface,@int,community)}
#     '''   
#     neighbor_info = {}
#     #this part generates a dict of all router objects, which to be used to get easily the router object by its id
#     #if this part will be used frequently, it is better to put it in a separate function
#     dict_routers = {}
#     for As in dict_as.values():
#         for router_id,router in As.routers.items():
#             dict_routers[router_id] = router
    
#     for As in dict_as.values():
#         for (r1,int1),(r2,int2) in As.link_dict.items():
#             if As.routers.get(r1) == None or As.routers.get(r2) == None: #means interconnection with other AS
#                 if dict_routers[r1].position != dict_routers[r2].position:
                    
#                     ABR_int_address1 = dict_routers[r1].interfaces.get(int1).address_ipv6_global
#                     ABR_int_address2 = dict_routers[r2].interfaces.get(int2).address_ipv6_global
#                     serve1 = dict_routers[r1].interfaces.get(int1).serve
#                     serve2 = dict_routers[r2].interfaces.get(int2).serve
                    
#                     neighbor_info[(dict_routers[r1].position, r1, int1, ABR_int_address1, serve1)] = (dict_routers[r2].position, r2, int2, ABR_int_address2, serve2)
#                     neighbor_info[(dict_routers[r2].position, r2, int2, ABR_int_address2, serve2)] = (dict_routers[r1].position, r1, int1, ABR_int_address1, serve1)
#     return neighbor_info

   
# def find_eBGP_neighbor_info(r,int,neighbor_info): #int(str) = interface.name
#     '''
#     For one particular ABR, find the info of its ebgp interface. RETURN: (As,router,ABR_interface,@int,community)
#     '''  
#     for key,value in neighbor_info.items():
#         if key[1] == r and key[2]==int:
#             return value
#     return('not found')

# def find_As_neighbor(As,dict_as):
#     """find all the As neighbors of an As from its link_dict. RETURN: {r.id : [(As.community, As.community_number),..]}"""
#     As_neighbor = {}
#     for (r1,_),(r2,_) in As.link_dict.items(): # find router r2, that is not in the As but connected to it
#         if r2 not in As.routers.keys():
#             if As_neighbor.get(r1) is None:
#                 As_neighbor[r1] = []
#             for As2 in dict_as.values():
#                 if r2 in As2.routers.keys(): # find the As where the router is located
#                     As_neighbor[r1].append((As2.community, As2.community_number))
#         elif r1 not in As.routers.keys():
#             if As_neighbor.get(r2) is None:
#                 As_neighbor[r2] = []
#             for As2 in dict_as.values():
#                 if r1 in As2.routers.keys():
#                     As_neighbor[r2].append((As2.community, As2.community_number))
#     if len(As_neighbor) == 0:
#         raise Exception("No As neighbor found, the As is isolated")
#     return As_neighbor

def find_CE_PE_link(dict_as):
    CE_PE_link = {}
    for router in dict_as["as1"]: # as1 is the core
        if router.type == "PE":
            for interface in router.interfaces.values():
                if interface.egp_protocol_type == "eBGP":
                    ce_id = interface.connected_router
                    ce_int = interface.connected_interface
                    for As in dict_as.values():
                        if ce_id in As.routers.keys():
                            CE = As.routers[ce_id]
                            for int in CE.interfaces.values():
                                if int.name == ce_int:
                                    CE_PE_link[(router.router_id,
                                                interface.address_ipv4)] = (ce_id, CE.type , int.address_ipv4)
    return CE_PE_link

#cepelink the result of find_CE_PE_link
def enable_vrf(As, cepelink, reg): #As should only be the core
    for router in As.routers.values():
        if router.type == "PE":
            for (pe_id,_), (ce_id, ce_type, _) in cepelink.items():
                reg.write(router.name, 1, "ip vrf " + ce_type)
                reg.write(router.name, 1, " rd " + str(ce_id) + ":" + str(pe_id))
                reg.write(router.name, 1, " route-target export " + str(ce_id) + ":" + str(pe_id))
                reg.write(router.name, 1, " route-target import " + str(ce_id) + ":" + str(pe_id))
                reg.write(router.name, 1, "!")
# ip vrf orange
#  rd 123:1
#  route-target export 123:1
#  route-target import 123:2
# !
#TODO verify the route-target import and export



def as_enable_BGP(dict_as, neighbor_info, reg):
    """
    Implement BGP for all As
    """
    order = 2
    PEs = []
    #TODO for CE
    for As in dict_as.values():
        for router in As.routers.values():
            if router.type == "PE":
                PEs.append([router.name, router.router_id])
        for [name,id] in PEs:
            reg.write(name, order, "router bgp " + str(As.as_id))
            reg.write(name, order, "bgp router-id " + id)
            reg.write(name, order, "no bgp default ipv4-unicast")
            reg.write(name, order, "bgp log-neighbor-changes")
            for [_,id] in PEs:
                if id != router.router_id:
                    loopback = id # we defined loopback as router_id
                    reg.write(name, order, "neighbor " + loopback + " remote-as " + str(As.as_id))
                    reg.write(name, order, "neighbor " + loopback + " update-source Loopback0")
                    reg.write(name, order, "!")
                    reg.write(name, order, "address-family vpnv4")
                    reg.write(name, order, "neighbor " + loopback + " activate")
                    reg.write(name, order, "neighbor " + loopback + " send-community extended")
                    reg.write(name, order, "exit-address-family")
                    reg.write(name, order, "!")
            
#  router bgp 123
#  bgp router-id 1.1.1.1
#  no bgp default ipv4-unicast
#  bgp log-neighbor-changes
#  neighbor 4.4.4.4 remote-as 123
#  neighbor 4.4.4.4 update-source Loopback0
#  !
#  address-family vpnv4
#   neighbor 4.4.4.4 activate
#   neighbor 4.4.4.4 send-community extended
#  exit-address-family
#  !            

#TODO VRF
#   address-family ipv4 vrf sfr
#   neighbor 10.1.12.2 remote-as 20
#   neighbor 10.1.12.2 activate
#   neighbor 10.1.12.2 as-override
#   no synchronization
#  exit-address-family
#  !
#  address-family ipv4 vrf orange
#   neighbor 10.0.12.2 remote-as 10
#   neighbor 10.0.12.2 activate
#   neighbor 10.0.12.2 as-override
#   no synchronization
#  exit-address-family
# !







#TODO
'''
functions particularly related to complete the configuration
'''
def as_config_interfaces(dict_as,reg):
    """default config of interfaces of all routers in all As"""
    for As in dict_as.values():
        for router in As.routers.values():
            for interface in router.interfaces.values():
                if interface.statu == "up":
                    reg.write(router.name,interface.name,"no ip address")
                    reg.write(router.name,interface.name,"negotiation auto")
                    reg.write(router.name,interface.name,"ipv6 address "+str(interface.address_ipv6_global)+str('/64'))

def as_config_unused_interface_and_loopback0(dict_as,reg): #dont call this function if you want to use telnet
    """default config of unused interfaces and loopback0 of all routers in all As"""
    for As in dict_as.values():
        for router in As.routers.values():
            reg.write(router.name,"Loopback0","no ip address")
            reg.write(router.name,"Loopback0","ipv6 address "+str(router.loopback))
            reg.write(router.name,"Loopback0","ipv6 enable")
            
            for interface in router.interfaces.values():
                if interface.statu == "down":
                    reg.write(router.name, interface.name, "no ipv6 address")
                    reg.write(router.name, interface.name, "shutdown")
                    reg.write(router.name, interface.name, "negotiation auto")
