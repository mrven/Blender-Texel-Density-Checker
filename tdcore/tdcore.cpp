#include "tdcore.h"
#include <cmath>
#include <iostream>
#include <vector>

#ifdef _WIN32
    #include <windows.h> // Windows
#endif

EXPORT_API void CalculateTDAreaArray(float *UVs, int UVCount, float *Areas, int *VertexCount, int PolyCount, float Scale, int Units, float *Result) 
{
    int VertexIndex = 0;

    for (int i = 0; i < PolyCount; i++) 
    {
        // Calculate UV Area
        float PolyUVArea = 0.f;
        float PolyTexelDensity = 0.f;

        if (VertexCount[i] > 2) 
        {
            for (int j = 1; j < VertexCount[i] - 1; ++j) 
            {
                float x1 = UVs[VertexIndex];
                float y1 = UVs[VertexIndex + 1];

                float x2 = UVs[VertexIndex + j * 2];
                float y2 = UVs[VertexIndex + j * 2 + 1];

                float x3 = UVs[VertexIndex + (j + 1) * 2];
                float y3 = UVs[VertexIndex + (j + 1) * 2 + 1];

                float area = std::abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1));
                PolyUVArea += 0.5 * area;
            }
        }

        float PolyGeometryArea = Areas[i];

        if (PolyUVArea > 0.f && PolyGeometryArea > 0.f) 
        {
            PolyTexelDensity =  Scale * std::sqrt(PolyUVArea) / std::sqrt(PolyGeometryArea);
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
