#include "tdcore.h"
#include <cmath>
#include <iostream>
#include <vector>

#ifdef _WIN32
    #include <windows.h> // Windows
#endif

EXPORT_API void CalculateGeometryAreas(float *Vertices, float *WorldMatrix, int VertexCount, int PolyCount, int *PerPolyVertexCount, float *Result) 
{
    CalculateGeometryAreas_Internal(Vertices, WorldMatrix, VertexCount, PolyCount, PerPolyVertexCount, Result);
}

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
    int ScaleMode,
    float* Result
)
{
    std::vector<float> TempTDsAreas(PolyCount * 2, 0.0f);
    CalculateTDAreaArray_Internal(
        UVs, UVCount, Areas, VertexCount, PolyCount, TextureXSize, TextureYSize, ScaleLength, Units, TempTDsAreas.data()
    );

    float TotalTDResult[2] = { 0.0f, 0.0f };
    CalculateTotalTDArea_Internal(TempTDsAreas.data(), SelectedPoly, PolyCount, TotalTDResult);
    float CurrentTD = TotalTDResult[0];
    float TotalUVArea = TotalTDResult[1];

    if (TotalUVArea > 0.0f)
    {

        float ScaleFactor = TargetTD / CurrentTD;
        
        // Target TD -0.5 is half TD; -2.0 is double TD 
        if (TargetTD < -1.0f)
            ScaleFactor = 2.0f;
        else if (TargetTD < 0.0f)
            ScaleFactor = 0.5f;

        int VertexIndex = 0;
        for (int i = 0; i < PolyCount; i++)
        {
            for (int j = 0; j < VertexCount[i]; j++) 
            {
                int Index = VertexIndex + j * 2;

                if (SelectedPoly[i] > 0) {
                  Result[Index] = OriginCoordinates[0] + (UVs[Index] - OriginCoordinates[0]) * ScaleFactor;
                  Result[Index + 1] = OriginCoordinates[1] + (UVs[Index + 1] - OriginCoordinates[1]) * ScaleFactor;
                } 
                else 
                {
                  Result[Index] = UVs[Index];
                  Result[Index + 1] = UVs[Index + 1];
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


EXPORT_API void CalculateGeometryAreas_Internal(float* Vertices, float* WorldMatrix, int VertexCount, int PolyCount, int* PerPolyVertexCount, float* Result)
{
    if (!Vertices || !WorldMatrix || !PerPolyVertexCount || !Result || VertexCount <= 0 || PolyCount <= 0)
        return;

    // Apply world matrix to all vertices
    std::vector<float> worldVerts(VertexCount * 3);
    for (int i = 0; i < VertexCount; ++i) {
      int base = i * 3;
      float x = Vertices[base];
      float y = Vertices[base + 1];
      float z = Vertices[base + 2];

      worldVerts[base] = WorldMatrix[0] * x + WorldMatrix[4] * y + WorldMatrix[8] * z + WorldMatrix[12];
      worldVerts[base + 1] = WorldMatrix[1] * x + WorldMatrix[5] * y + WorldMatrix[9] * z + WorldMatrix[13];
      worldVerts[base + 2] = WorldMatrix[2] * x + WorldMatrix[6] * y + WorldMatrix[10] * z + WorldMatrix[14];
    }
    
    int vertexIndex = 0;

    for (int i = 0; i < PolyCount; ++i) {
      float area = 0.f;
      int polyVertCount = PerPolyVertexCount[i];

      if (polyVertCount < 3 || vertexIndex + polyVertCount > VertexCount) {
        Result[i] = 0.0f;
        vertexIndex += polyVertCount;
        continue;
      }

      float *v0 = &worldVerts[vertexIndex * 3];

      for (int j = 1; j < polyVertCount - 1; ++j) {
        float *v1 = &worldVerts[(vertexIndex + j) * 3];
        float *v2 = &worldVerts[(vertexIndex + j + 1) * 3];

        float ux = v1[0] - v0[0];
        float uy = v1[1] - v0[1];
        float uz = v1[2] - v0[2];

        float vx = v2[0] - v0[0];
        float vy = v2[1] - v0[1];
        float vz = v2[2] - v0[2];

        float cx = uy * vz - uz * vy;
        float cy = uz * vx - ux * vz;
        float cz = ux * vy - uy * vx;

        float triangleArea = 0.5f * sqrtf(cx * cx + cy * cy + cz * cz);
        area += triangleArea;
      }

      Result[i] = area;
      vertexIndex += polyVertCount;
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
