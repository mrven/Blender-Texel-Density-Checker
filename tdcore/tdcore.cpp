#include "tdcore.h"
#include <cmath>
#include <iostream>

#ifdef _WIN32
    #include <windows.h> // Windows
#endif

void CalculateTDAreaArray(
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
) 
{ 
    CalculateTDAreaArray_Internal(UVs, UVCount, Areas, VertexCount, PolyCount, TextureXSize, TextureYSize, ScaleLength, Units, Result);
}

EXPORT_API void CalculateTotalTDArea(float* TDsAreas, unsigned char* SelectedPoly, int PolyCount, float* Result)
{
    float TotalTD = 0;
    float TotalUVArea = 0;
    for (int i = 0; i < PolyCount; i++)
    {
        if (SelectedPoly[i] > 0)
        {
            TotalTD += TDsAreas[i * 2];
            TotalUVArea += TDsAreas[i * 2 + 1];
        }
    }

    Result[0] = TotalTD;
    Result[1] = TotalUVArea;
}

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
)
{
    // Aspect Ratio
    float AspectRatio = static_cast<float>(TextureXSize) / static_cast<float>(TextureYSize);

    if (AspectRatio < 1)
    {
        AspectRatio = 1 / AspectRatio;
    }

    int LargestSide = (TextureXSize > TextureYSize) ? TextureXSize : TextureYSize;

    int VertexIndex = 0;

    for (int i = 0; i < PolyCount; i++)
    {
        // Calculate UV Area
        float PolyUVArea = 0.f;
        float PolyTexelDensity = 0.f;

        if (VertexCount[i] > 2)
        {
            float UVX1 = UVs[VertexIndex];
            float UVY1 = UVs[VertexIndex + 1];
            float UVX2 = UVs[VertexIndex + 2];
            float UVY2 = UVs[VertexIndex + 3];
            float UVX3 = UVs[VertexIndex + 4];
            float UVY3 = UVs[VertexIndex + 5];

            float Area = std::abs((UVX2 - UVX1) * (UVY3 - UVY1) - (UVX3 - UVX1) * (UVY2 - UVY1));
            PolyUVArea += Area;
        }

        float PolyGeometryArea = Areas[i];

        if (PolyUVArea > 0.f && PolyGeometryArea > 0.f)
        {
            PolyTexelDensity = ((LargestSide / std::sqrt(AspectRatio)) * std::sqrt(PolyUVArea)) /
                               (std::sqrt(PolyGeometryArea) * 100) / ScaleLength;
        }
        else
        {
            PolyTexelDensity = 0.0001f;
        }

        switch (Units)
        {
            case 1:
                PolyTexelDensity *= 100.f;
                break;
            case 2:
                PolyTexelDensity *= 2.54f;
                break;
            case 3:
                PolyTexelDensity *= 30.48f;
                break;
            default:
                break;
        }

        Result[i * 2] = PolyTexelDensity;
        Result[i * 2 + 1] = PolyUVArea;

        VertexIndex += VertexCount[i] * 2;
    }
}

// Optional Entry Point (Windows)
#ifdef _WIN32
    BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
    {
        switch (ul_reason_for_call)
        {
            case DLL_PROCESS_ATTACH:
            case DLL_THREAD_ATTACH:
            case DLL_THREAD_DETACH:
            case DLL_PROCESS_DETACH:
                break;
        }
        return TRUE;
    }
#endif
