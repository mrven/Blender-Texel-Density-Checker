# Blender Addon: Texel Density Checker

![Header](/images/header.png)

**[English README](/README.md)**


Texel Density Checker – Аддон для Blender, который позволяет расчитывать и задавать размер текселя на модели. 

***Units*** – Единицы измерения текселя: **px/cm**, **px/m**, **px/in**, **px/ft**.

![Different Units](/images/units.gif)

***Texture Size*** – Размер текстуры, относительно которой будет расчитываться тексель. Для удобства, в выпадающем списке присутсвуют предустановки квадратных текстур 512 – 4096 пикселей. Также есть возможность задания произвольного размера текстуры. Для этого в списке необходимо выбрать пункт “Custom” и ввести вручную размеры. Также поддерживаются неквадратные размеры текстур.

![Texture Size](/images/texture_size_1.png)
![Texture Size](/images/texture_size_2.png)

***Texel Density*** – Текущее значение текселя. Это значение расчитывается по нажатию кнопки “Calculate TD” и представляет собой СРЕДНЕЕ значение островов развёртки всей модели (при расчёте в объектном режиме) или выделенных полигонов (в режиме редактирования при включенной опции “Selected Faces”).

![Calculate TD](/images/calculate_td.gif)

***Set Texel Density*** – Установка заданного значения текселя. Аддон расчитывает текущее значение текселя, сравнивает его с заданным, и ссответственно, масштабирует острова развёртки так, чтобы получить заданный тексель.

![Set TD](/images/set_td.gif)

***Set Method*** – Метод масштабирования островов при установке Texel Density. **Each** - Каждый остров будет отмасшабирован до достижения необходимого значения Texel Density; **Average** - Острова будут отмасшабированы пропорционально до достижения среднего значения Texel Density.

![Set TD Method](/images/set_td_method.gif)

***Calc -> Set Value*** – Cкопировать значение из поля “Calculate TD” в поле “Set TD”.

![Calc To Set](/images/copy_calc_to_set.gif)


***Кнопки пресетов*** для быстрой установки текселя.

![Peset Buttons](/images/presets.gif)

***TD from Active to Others*** – Копирование значение текселя с активного на выделенные в объектном режиме.

![Copy TD](/images/copy_td.gif)

***Filled UV Space*** – Процент заполненности текстуры. Это значение может превышать 100%, если на развёртке имеется много наложенных друг на друга островов (overlaped). Это значение носит справочный характер.

![Filled UV Space](/images/filled_uv.png)

***Select Faces with same TD*** – Выбрать полигоны с одинаковым значением Texel Density. Порог значения для выбора задаётся значением **Select Threshold**.

![Select Faces](/images/select_same_td.gif)