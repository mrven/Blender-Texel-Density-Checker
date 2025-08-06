[<< Return to README](../README.md#documentation)

# Texel Units and Texture Size

This section defines how texel density is calculated, based on the measurement units and texture resolution.

# UI Elements and Functionality

![Texel Units](./images/ui/texel_units_panel.png)

![Texel Units Custom](./images/ui/texel_units_custom_panel.png)

### Units

Sets the unit of measurement for texel density calculations.

| Value | Description           |
|-------|-----------------------|
| px/cm | pixels per centimeter | 
| px/m  | pixels per meter      |
| px/in | pixels per inch       |
| px/ft | pixels per feat       |

### Texture Size

Defines the resolution of the texture for density calculations.

| Value         | Description                                                           |
|---------------|-----------------------------------------------------------------------|
| 512 - 4096 px | common square of two texture sizes (512, 1024, 2048, 4096)            | 
| Custom        | Show input fields for non-standard (or non-square) texture dimensions |

### Width (Custom Size only)

Width of texture in pixels if select Custom Texture Size option.

### Height (Custom Size only)

Height of texture in pixels if select Custom Texture Size option.