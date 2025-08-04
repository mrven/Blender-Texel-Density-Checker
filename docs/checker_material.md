[<< Return to README](../README.md#documentation)

# Interactive Checker Material

This feature is assignment Material with checker texture. Texture dynamically changes if you change "Texture Size" on Texel Units and Texture Size UI Panel. Also this material visualize data from [Bake TD/UV/Islands to Vertex Color](bake_td.md) operator.

# UI Elements and Functionality

![Checker Material](./images/ui/checker_material_panel.png)

### Checker Method

How Checker Material assignment works.

| Value             | Description                                                                                                                                                                                                         |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Store and Replace | Save assignments of current materials on object. Then Checker material is assigned to object and applied to all faces. Restore Materials button is restore saved materials and delete Checker Material from object. | 
| Replace           | Remove all materials from object and assign Checker Material to all faces.                                                                                                                                          |

### Checker Type

Type of Checker Texture.

| Value      | Description                                     |
|------------|-------------------------------------------------|
| Color Grid | Blender's default procedural Color Grid texture | 
| UV Grid    | Blender's default procedural UV Grid texture    |

### UV Scale

Additional UV scale for Checker Texture.

### Assign Checker Material

Assign Checker Material to selected object. For show Checker Material you need to change Viewport Shading to "Material Preview".

### Restore Materials (Store and Replace method only)

Restore saved materials and delete Checker Material from object.

### Clear Stored Materials (Store and Replace method only)

Clear saved materials from selected object. 

> [!CAUTION]
> This operation may lose saved materials.

# Usage Examples