# Blender Addon: Texel Density Checker

![Header](/images/header.png)

**[Russian README](/README_ru.md)**

With **Texel Density Checker** you can: 

* Calculate Texel Density for model for different texture size (includes non-squared textures and custom size)
* Rescale UV for getting texel density what you want
* Copy Texel Density from one object to others
* Select faces for same Density

Texel Density Checker simple for use. You need select your mesh (or faces) and texture size and just click button.

***Units*** – Different Texel Density units: **px/cm**, **px/m**, **px/in**, **px/ft**.

![Different Units](/images/units.gif)

***Texture Size*** – Texture Size for calculation Texel Density. Parameter have presets for squared textures. Also you can set custom size (select "Custom"). Supports any aspect ratio.

![Texture Size](/images/texture_size_1.png)
![Texture Size](/images/texture_size_2.png)

***Texel Density*** – Current Texel's value. This value calculate with click button "Calculate TD". It is average value all or selected UV islands.

![Calculate TD](/images/calculate_td.gif)

***Set Method*** – Set TD Methods. **Each** - Each island will be rescale individually; **Average** - All islands will be rescale proportionally.

![Set TD Method](/images/set_td_method.gif)

***Calc -> Set Value*** – Copy Value from “Calculate TD” to “Set TD” text field.

![Calc To Set](/images/copy_calc_to_set.gif)


***Peset Buttons*** for Quick Set Texel Density.

![Peset Buttons](/images/presets.gif)

***TD from Active to Others*** – Copy TD Value from Active to Selected Object.

![Copy TD](/images/copy_td.gif)

***Filled UV Space*** – The percentage of filling UV Space. This value can be greater than 100%. This value is for reference only.

![Filled UV Space](/images/filled_uv.png)

***Select Faces with same TD*** – Select Faces with same Texel Density. Select only one face and click Button.

![Select Faces](/images/select_same_td.gif)