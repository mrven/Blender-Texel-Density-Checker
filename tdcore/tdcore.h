#pragma once

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
#ifdef __cplusplus
}
#endif
