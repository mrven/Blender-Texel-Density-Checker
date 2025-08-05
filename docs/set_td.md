[<< Return to README](../README.md#documentation)

# Set Texel Density

The Set Texel Density operator is used to set the texel density for selected UV islands or the entire object based on target value. This feature is essential for ensuring consistent texture detail and scale across your models, especially for game assets or high-fidelity renders.

# UI Elements and Functionality

![Set TD](./images/ui/set_td_panel.png)

### Selected Faces (Edit mode only)

Toggle to limit set operation to selected faces in Edit Mode. If Selected Faces is disabled, the operator processes the entire object.

### Set TD

Texel Density value to be set.

### Set Method

Different options for scaling UV islands for getting of target TD.

| Value   | Description                                                                          |
|---------|--------------------------------------------------------------------------------------|
| Each    | Calculate and Set TD for each UV islands individually.                               | 
| Average | Calculate and Set average TD for all UV islands. This option keep UV islands ratios. |

### Scale Anchor

Origin point for scaling UV islands.

| Value           | Description                                  |
|-----------------|----------------------------------------------|
| Selection       | Median point for each object                 | 
| UV Center       | Center of UV coordinates (0.5, 0.5)          |
| UV Left Bottom  | Left Bottom Corner of UV coordinates (0, 0)  |
| UV Left Top     | Left Top Corner of UV coordinates (0, 1)     |
| UV Right Bottom | Right Bottom Corner of UV coordinates (1, 0) |
| UV Right Top    | Right Top Corner of UV coordinates (1, 1)    |
| 2D Cursor       | Coordinates of 2D Cursor in UV Editor        |

### Set TD

Run Set Texel Density operator.

### Presets Value Buttons

Set Texel Density to preset values. Preset Values depends on selected units.

### Half/Double TD

Set Texel Density to half or double of current value.

### TD from Active to Others (Object mode only)

Calculate Texel Density for active object and set it to other selected objects.

# Usage Examples

![Set TD](./images/gifs/set_td.gif)