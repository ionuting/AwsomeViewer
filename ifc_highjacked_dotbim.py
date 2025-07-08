import ifcopenshell
import uuid
import json

def create_guid():
    """Generate a GUID for IFC entities."""
    return str(uuid.uuid4())

def create_mesh_json():
    """Create a JSON mesh representation for IfcWall and IfcColumn."""
    # Define simple mesh data (box for wall, prism for column)
    wall_vertices = [
        # Bottom face
        0.0, 0.0, 0.0,  # 0
        2.0, 0.0, 0.0,  # 1
        2.0, 0.3, 0.0,  # 2
        0.0, 0.3, 0.0,  # 3
        # Top face
        0.0, 0.0, 3.0,  # 4
        2.0, 0.0, 3.0,  # 5
        2.0, 0.3, 3.0,  # 6
        0.0, 0.3, 3.0   # 7
    ]
    wall_indices = [
        # Bottom
        0, 1, 2, 2, 3, 0,
        # Top
        4, 5, 6, 6, 7, 4,
        # Sides
        0, 1, 5, 5, 4, 0,
        1, 2, 6, 6, 5, 1,
        2, 3, 7, 7, 6, 2,
        3, 0, 4, 4, 7, 3
    ]
    column_vertices = [
        # Bottom face
        4.0, 0.0, 0.0,  # 0
        4.5, 0.0, 0.0,  # 1
        4.5, 0.5, 0.0,  # 2
        4.0, 0.5, 0.0,  # 3
        # Top face
        4.0, 0.0, 4.0,  # 4
        4.5, 0.0, 4.0,  # 5
        4.5, 0.5, 4.0,  # 6
        4.0, 0.5, 4.0   # 7
    ]
    column_indices = [
        # Bottom
        0, 1, 2, 2, 3, 0,
        # Top
        4, 5, 6, 6, 7, 4,
        # Sides
        0, 1, 5, 5, 4, 0,
        1, 2, 6, 6, 5, 1,
        2, 3, 7, 7, 6, 2,
        3, 0, 4, 4, 7, 3
    ]

    # Create .dotbim-like JSON structure
    mesh_data = {
        "meshes": [
            {
                "mesh_id": 0,
                "coordinates": wall_vertices,
                "indices": wall_indices
            },
            {
                "mesh_id": 1,
                "coordinates": column_vertices,
                "indices": column_indices
            }
        ],
        "elements": [
            {
                "mesh_id": 0,
                "guid": create_guid(),
                "type": "IfcWall",
                "color": {"r": 200, "g": 200, "b": 200, "a": 255},
                "info": {"Name": "Wall_1", "Type": "Standard Wall"},
                "vector": {"x": 0.0, "y": 0.0, "z": 0.0},
                "rotation": {"qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0}
            },
            {
                "mesh_id": 1,
                "guid": create_guid(),
                "type": "IfcColumn",
                "color": {"r": 150, "g": 150, "b": 150, "a": 255},
                "info": {"Name": "Column_1", "Type": "Concrete Column"},
                "vector": {"x": 4.0, "y": 0.0, "z": 0.0},
                "rotation": {"qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0}
            }
        ]
    }
    return json.dumps(mesh_data)

def create_ifc_with_objects_and_mesh():
    # Create a new IFC file with IFC4 schema
    ifc_file = ifcopenshell.file(schema="IFC4")

    # Create basic IFC structure
    owner_history = ifc_file.create_entity("IfcOwnerHistory")
    project = ifc_file.create_entity("IfcProject", GlobalId=create_guid(), Name="My Project")
    site = ifc_file.create_entity("IfcSite", GlobalId=create_guid(), Name="My Site")
    building = ifc_file.create_entity("IfcBuilding", GlobalId=create_guid(), Name="My Building")
    storey = ifc_file.create_entity("IfcBuildingStorey", GlobalId=create_guid(), Name="Level 1", Elevation=0.0)

    # Create spatial hierarchy
    ifc_file.create_entity("IfcRelAggregates", GlobalId=create_guid(), RelatingObject=project, RelatedObjects=[site])
    ifc_file.create_entity("IfcRelAggregates", GlobalId=create_guid(), RelatingObject=site, RelatedObjects=[building])
    ifc_file.create_entity("IfcRelAggregates", GlobalId=create_guid(), RelatingObject=building, RelatedObjects=[storey])

    # Create IfcWall
    wall = ifc_file.create_entity("IfcWall", GlobalId=create_guid(), Name="Wall_1", OwnerHistory=owner_history)
    ifc_file.create_entity("IfcRelContainedInSpatialStructure", GlobalId=create_guid(), RelatingStructure=storey, RelatedElements=[wall])

    # Add Pset_WallCommon
    wall_pset = ifc_file.create_entity("IfcPropertySet", GlobalId=create_guid(), Name="Pset_WallCommon")
    ifc_file.create_entity("IfcRelDefinesByProperties", GlobalId=create_guid(), RelatingPropertyDefinition=wall_pset, RelatedObjects=[wall])
    wall_properties = [
        ifc_file.create_entity("IfcPropertySingleValue", Name="Reference", NominalValue=ifc_file.create_entity("IfcLabel", "WAL001")),
        ifc_file.create_entity("IfcPropertySingleValue", Name="IsExternal", NominalValue=ifc_file.create_entity("IfcBoolean", True)),
        ifc_file.create_entity("IfcPropertySingleValue", Name="LoadBearing", NominalValue=ifc_file.create_entity("IfcBoolean", True)),
        ifc_file.create_entity("IfcPropertySingleValue", Name="FireRating", NominalValue=ifc_file.create_entity("IfcLabel", "FR-60"))
    ]
    wall_pset.HasProperties = wall_properties

    # Create IfcColumn
    column = ifc_file.create_entity("IfcColumn", GlobalId=create_guid(), Name="Column_1", OwnerHistory=owner_history)
    ifc_file.create_entity("IfcRelContainedInSpatialStructure", GlobalId=create_guid(), RelatingStructure=storey, RelatedElements=[column])

    # Add Pset_ColumnCommon
    column_pset = ifc_file.create_entity("IfcPropertySet", GlobalId=create_guid(), Name="Pset_ColumnCommon")
    ifc_file.create_entity("IfcRelDefinesByProperties", GlobalId=create_guid(), RelatingPropertyDefinition=column_pset, RelatedObjects=[column])
    column_properties = [
        ifc_file.create_entity("IfcPropertySingleValue", Name="Reference", NominalValue=ifc_file.create_entity("IfcLabel", "COL001")),
        ifc_file.create_entity("IfcPropertySingleValue", Name="IsExternal", NominalValue=ifc_file.create_entity("IfcBoolean", False)),
        ifc_file.create_entity("IfcPropertySingleValue", Name="LoadBearing", NominalValue=ifc_file.create_entity("IfcBoolean", True)),
        ifc_file.create_entity("IfcPropertySingleValue", Name="Slope", NominalValue=ifc_file.create_entity("IfcReal", 0.0))
    ]
    column_pset.HasProperties = column_properties

    # Create custom mesh JSON
    mesh_json = create_mesh_json()

    # Add custom mesh as a property to both objects
    for entity in [wall, column]:
        custom_pset = ifc_file.create_entity("IfcPropertySet", GlobalId=create_guid(), Name="Pset_CustomGeometry")
        ifc_file.create_entity("IfcRelDefinesByProperties", GlobalId=create_guid(), RelatingPropertyDefinition=custom_pset, RelatedObjects=[entity])
        mesh_property = ifc_file.create_entity("IfcPropertySingleValue", Name="Custom_Mesh", NominalValue=ifc_file.create_entity("IfcText", mesh_json))
        custom_pset.HasProperties = [mesh_property]

    # Save the IFC file
    ifc_file.write("output.ifc")

    print("✅ IFC file created: output.ifc")
    print("\n📋 Mesh JSON representation:")
    print(json.dumps(json.loads(mesh_json), indent=2))

if __name__ == "__main__":
    create_ifc_with_objects_and_mesh()
