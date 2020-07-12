# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Generate unique id for topology entity"""

class ID_GEN:
    """Generate unique id for Topology entites
    
    Attributes
    ----------
    topology_id: str
        Id prefixed for each topology entity
    counter: int
        Unique identifier of an entity within a topology
    is_unique_id: bool
        If unique Id's should be used for entity names
        (default is True)

    """
    topology_id = ""
    counter = 0
    is_unique_id = True

    def __init__(self, topology_id):
        """Initialize `topology_id`

        Parameters
        ----------
        topology_id: str

        """
        ID_GEN.topology_id = topology_id

    @staticmethod
    def get_id(name):
        """Generate unique id on each call

        Parameters
        ----------
        name: str
            Name of the entity as shown to the user
        
        Returns
        -------
        str
            If `is_unique_id` is true, then an unique id is returned
            Else, `name` is returned back

        """
        if ID_GEN.is_unique_id:
            ID_GEN.counter += 1
            return ID_GEN.topology_id+"-"+str(ID_GEN.counter)
        else:
            return name

    @staticmethod
    def enable_unique_id():
        """
        If disabled, enable generation of unique id
        
        """
        ID_GEN.is_unique_id = True

    @staticmethod
    def disable_unique_id():
        """
        If enabled, disable generation of unique id
        
        """
        ID_GEN.is_unique_id = False
