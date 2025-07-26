#include "tdcore.h"
#include <iostream>

#ifdef _WIN32
    #include <windows.h> // Windows
#endif

EXPORT_API void CalculateTDAreaArray(float *UVs, int UVCount, float *Areas, int *VertexCount, int PolyCount, float Scale, int Units, float *Result) 
{
    int vertexIndex = 0;

    for (int i = 0; i < PolyCount; i++) 
    {
        // Calculate UV Area
        float polyUVArea = 0.f;
        float polyTexelDensity = 0.f;

        if (VertexCount[i] > 2) 
        {
            for (int j = 1; j < VertexCount[i] - 1; ++j) 
            {
                float x1 = UVs[vertexIndex];
                float y1 = UVs[vertexIndex + 1];

                float x2 = UVs[vertexIndex + j * 2];
                float y2 = UVs[vertexIndex + j * 2 + 1];

                float x3 = UVs[vertexIndex + (j + 1) * 2];
                float y3 = UVs[vertexIndex + (j + 1) * 2 + 1];

                float area = std::abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1));
                polyUVArea += 0.5 * area;
            }
        }

        float polyGeometryArea = Areas[i];

        if (polyUVArea > 0.f && polyGeometryArea > 0.f) 
        {
            polyTexelDensity =  Scale * std::sqrt(polyUVArea) / std::sqrt(polyGeometryArea);
        } 
        else 
        {
            polyTexelDensity = 0.0001f;
        }

        switch (Units) 
        {
            case 1:
                polyTexelDensity *= 100.f;
                break;
            case 2:
                polyTexelDensity *= 2.54f;
                break;
            case 3:
                polyTexelDensity *= 30.48f;
                break;
            default:
                break;
        }

        Result[i * 2] = polyTexelDensity;
        Result[i * 2 + 1] = polyUVArea;

        vertexIndex += VertexCount[i] * 2;
    }
}

EXPORT_API void ValueToColor(float *Values, int ValuesCount, float RangeMin, float RangeMax, float *Result) 
{
    for (int i = 0; i < ValuesCount; i++) 
    {
  
        float remappedValue = 0.5f;

        if (std::abs(RangeMax - RangeMin) > 0.001f) 
        {
            remappedValue = Saturate((Values[i] - RangeMin) / (RangeMax - RangeMin));
        }

        float hue = (1.0f - remappedValue) * 0.67f;
        float r, g, b;
        HSVtoRGB(hue, 1.0f, 1.0f, r, g, b);

        Result[i * 4] = r;
        Result[i * 4 + 1] = g;
        Result[i * 4 + 2] = b;
        Result[i * 4 + 3] = 1.0f;
    }
}

void HSVtoRGB(float h, float s, float v, float &r, float &g, float &b) 
{
    float c = v * s;
    float hPrime = h * 6.0f;
    float x = c * (1 - std::fabs(fmod(hPrime, 2.0f) - 1));
    float m = v - c;

    if (0 <= hPrime && hPrime < 1) 
    {
        r = c; g = x; b = 0;
    } else if (1 <= hPrime && hPrime < 2) 
    {
        r = x; g = c; b = 0;
    } else if (2 <= hPrime && hPrime < 3) 
    {
        r = 0; g = c; b = x;
    } else if (3 <= hPrime && hPrime < 4) 
    {
        r = 0; g = x; b = c;
    } else if (4 <= hPrime && hPrime < 5) 
    {
        r = x; g = 0; b = c;
    } else if (5 <= hPrime && hPrime < 6) 
    {
        r = c; g = 0; b = x;
    } else 
    {
        r = g = b = 0;
    }

    r += m;
    g += m;
    b += m;
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
