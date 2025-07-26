#pragma once
#include <cmath>

#ifdef _WIN32
    #define EXPORT_API __declspec(dllexport)
#else
    #define EXPORT_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C"
{
#endif
    EXPORT_API void CalculateTDAreaArray(float *UVs, int UVCount, float *Areas, int *VertexCount, int PolyCount, float Scale, int Units, float *Result);

    EXPORT_API void ValueToColor(float* Values, int ValuesCount, float RangeMin, float RangeMax, float* Result);

    inline float Saturate(float x) {return std::fmax(0.0f, std::fmin(1.0f, x));}

    void HSVtoRGB(float h, float s, float v, float &r, float &g, float &b);
#ifdef __cplusplus
}
#endif
