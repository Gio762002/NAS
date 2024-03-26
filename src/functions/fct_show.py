'''
functions that show the results of the analysis, help to test.
'''
def show_as_router_address(As):
    print("AS",As.as_id,"address plan:")
    for router in As.routers.values():
        for interface in router.interfaces.keys(): #interface as a string
            print(router.router_id,":",interface,':',router.interfaces[interface].address_ipv4,"TO", router.interfaces[interface].connected_router)
        print(" ")

def show_as_loopback_plan(As):
    print("AS",As.as_id,"loopback plan:")
    for router in As.routers.values():
        print(router.router_id,":",router.loopback)
    print("")

def show_as_link(As):
    for ((r1, i1),(r2, i2)) in As.link_dict.items():
        print(r1,":",i1,"<->",r2,":",i2)
    print("")