#pragma once

#ifdef __cplusplus
extern "C"
{
#endif
    __declspec(dllexport) void CalculateTDAreaArray(
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

#ifdef __cplusplus
}
#endif
