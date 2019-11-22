#version 330
#define MAX_POINTS 100
in vec3 vPos;
in vec2 vTex;


in float vNgt;
// in vec4 vColor;
// in float vDistortion;

// in float vSize;
// in float vRadius;
// in vec2 vCenter;
// in vec2 vPoints[MAX_POINTS];

uniform mat4 modelView;

out vec4 fCol;
out vec2 fTex;

out float fNgt;
// out vec4 fColor;
// out float fDistortion;

// out float fSize;
// out float fRadius;
// out vec2 fCenter;
// out vec2 fPoints[MAX_POINTS];

const int GAUSSIAN_SAMPLES = 18;

uniform float texelWidthOffset;
uniform float texelHeightOffset;

varying vec2 textureCoordinate;
varying vec2 blurCoordinates[GAUSSIAN_SAMPLES];

void main(void){
    gl_Position = modelView * vec4(vPos.xyz, 1.0);
    fTex = vTex;
    fCol = vec4(1.0, 1.0, 1.0, 1.0);

    fNgt = vNgt;
    // fColor = vColor;
    // fDistortion = vDistortion;

    // fSize = vSize;
    // fRadius = vRadius;
    // fCenter = vCenter;
    // fPoints = vPoints;


    // if (vDistortion > 0){
    //     gl_Position = position;
    //     textureCoordinate = inputTextureCoordinate.xy;

    //     // Calculate the positions for the blur
    //     int multiplier = 0;
    //     vec2 blurStep;
    //     vec2 singleStepOffset = vec2(texelHeightOffset, texelWidthOffset);

    //     for (int i = 0; i < GAUSSIAN_SAMPLES; i++)
    //     {
    //         multiplier = (i - ((GAUSSIAN_SAMPLES - 1) / 2));
    //         // Blur in x (horizontal)
    //         blurStep = float(multiplier) * singleStepOffset;
    //         blurCoordinates[i] = inputTextureCoordinate.xy + blurStep;
    //     }
    // }

}