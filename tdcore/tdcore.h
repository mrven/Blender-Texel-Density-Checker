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
    EXPORT_API void CalculateGeometryAreas(
        float *Vertices, 
        float *WorldMatrix,
        int VertexCount, 
        int PolyCount,
        int *PerPolyVertexCount, 
        float *Result
    );

    EXPORT_API void CalculateTDAreaArray(
        float* UVs,
        int UVCount,
        float* Areas,
        int* VertexCount,
        int PolyCount,
        int TextureXSize,
        int TextureYSize,
        float ScaleLength,
        int Units,
        float* Result
    );

    EXPORT_API void CalculateTotalTDArea(float* TDsAreas, unsigned char* SelectedPoly, int PolyCount, float* Result);

    EXPORT_API void SetTD(
        float* UVs,
        int UVCount,
        float* Areas,
        int* VertexCount,
        int PolyCount,
        int TextureXSize,
        int TextureYSize,
        float ScaleLength,
        int Units,
        unsigned char* SelectedPoly,
        float TargetTD,
        float* OriginCoordinates,
        int ScaleMode,
        float* Result
    );

    EXPORT_API void CalculateGeometryAreas_Internal(
        float *Vertices, 
        float *WorldMatrix,
        int VertexCount, 
        int PolyCount,
        int *PerPolyVertexCount,
        float *Result
    );

    EXPORT_API void CalculateTDAreaArray_Internal(
        float* UVs,
        int UVCount,
        float* Areas,
        int* VertexCount,
        int PolyCount,
        int TextureXSize,
        int TextureYSize,
        float ScaleLength,
        int Units,
        float* Result
    );

    EXPORT_API void CalculateTotalTDArea_Internal(float* TDsAreas, unsigned char* SelectedPoly, int PolyCount, float* Result);
#ifdef __cplusplus
}
#endif
