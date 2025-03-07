#include "tdcore.h"
#include <cmath>
#include <iostream>
#include <vector>

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
    CalculateTotalTDArea_Internal(TDsAreas, SelectedPoly, PolyCount, Result); 
}

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
    float* Result
)
{
    std::vector<float> TempTDsAreas(PolyCount * 2, 0.0f);
    CalculateTDAreaArray_Internal(
        UVs, UVCount, Areas, VertexCount, PolyCount, TextureXSize, TextureYSize, ScaleLength, Units, TempTDsAreas.data()
    );

    float TotalTDResult[2] = { 0.0f, 0.0f };
    CalculateTotalTDArea_Internal(TempTDsAreas.data(), SelectedPoly, PolyCount, TotalTDResult);
    float CurrentTD = std::round(TotalTDResult[0] * 1000.0f) / 1000.0f;
    float TotalUVArea = TotalTDResult[1];

    if (TotalUVArea > 0.0f)
    {
        float ScaleFactor = TargetTD / CurrentTD;

        int VertexIndex = 0;
        for (int i = 0; i < PolyCount; i++)
        {
            if (SelectedPoly[i] > 0)
            {
                for (int j = 0; j < VertexCount[i]; j++)
                {
                    int Index = VertexIndex + j * 2;
                    Result[Index] = OriginCoordinates[0] + (UVs[Index] - OriginCoordinates[0]) * ScaleFactor;
                    Result[Index + 1] = OriginCoordinates[1] + (UVs[Index + 1] - OriginCoordinates[1]) * ScaleFactor;
                }
            }
            VertexIndex += VertexCount[i] * 2;
        }
    }
    else
    {
        std::copy(UVs, UVs + UVCount * 2, Result);
    }
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

EXPORT_API void CalculateTotalTDArea_Internal(float* TDsAreas, unsigned char* SelectedPoly, int PolyCount, float* Result)
{
    float TotalTD = 0;
    float TotalUVArea = 0;
    for (int i = 0; i < PolyCount; i++)
    {
        if (SelectedPoly[i] > 0)
        {
            float UVArea = TDsAreas[i * 2 + 1];
            float TexelDensity = TDsAreas[i * 2];

            TotalUVArea += UVArea;
            TotalTD += TexelDensity * UVArea;
        }
    }

    if (TotalUVArea > 0)
    {
        TotalTD /= TotalUVArea;
    }

    Result[0] = TotalTD;
    Result[1] = TotalUVArea;
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
