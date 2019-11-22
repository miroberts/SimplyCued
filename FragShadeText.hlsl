#version 330
#define MAX_POINTS 100
in vec4 fCol;
in vec2 fTex;


in float fNgt;
// in vec4 fColor;
// in float fDistortion;

// in float fSize;
// in float fRadius;
uniform float fRadius;
// in vec2 fCenter;
uniform vec2 fCenter;
// in vec2 fPoints[MAX_POINTS];
uniform vec2 fPoints[MAX_POINTS];


uniform sampler2D samTex;

out vec4 FragColor;



const lowp int GAUSSIAN_SAMPLES = 18;

varying highp vec2 textureCoordinate;
varying highp vec2 blurCoordinates[GAUSSIAN_SAMPLES];




// http://geomalgorithms.com/a03-_inclusion.html
// Copyright 2000 softSurfer, 2012 Dan Sunday
// This code may be freely used and modified for any purpose
// providing that this copyright notice is included with it.
// SoftSurfer makes no warranty for this code, and cannot be held
// liable for any real or imagined damage resulting from its use.
// Users of this code must verify correctness for their application.

float isLeft( vec2 P0, vec2 P1, vec4 P2 )
{
    return ( (P1.x - P0.x) * (P2.y - P0.y) - (P2.x -  P0.x) * (P1.y - P0.y) );
}

int wn_PnPoly( vec4 P, float size)
{
    int wn = 0;

    for (int i=0; i<size; i++) {   
        if (fPoints[i].y <= P.y) {  
            if (fPoints[i+1].y  > P.y)    
                if (isLeft(fPoints[i], fPoints[i+1], P) > 0)  
                    ++wn;     
        }
        else {                       
            if (fPoints[i+1].y  <= P.y)    
                if (isLeft(fPoints[i], fPoints[i+1], P) < 0) 
                    --wn;  
        }
    }
    return wn;
}


// if there are 2 points it is a circle. 
// Three or more is polygon using wn_PnPoly        posibly use fast ball to speed up if more then 5 points
float squared(float x){
    return x * x;
}

// Find if point is included in circle.
bool included(vec4 qpoint){
    return (fRadius >= sqrt(squared(fCenter.x-qpoint.x)+squared(fCenter.y-qpoint.y)));
}

void main(void){
    
    FragColor = texture(samTex, fTex);

    // if(fSize >= 2) {
    //     if(included(FragColor)) {
    //         if (wn_PnPoly(FragColor, fSize) == 0){
    //             discard;
    //         }
    //     }
    //     else{
    //         discard;
    //     }
    // }

    // FragColor + fColor;
        // FragColor.x + fColor.x;
        // FragColor.x + fColor.y;
        // FragColor.z + fColor.z;
        // FragColor.w + fColor.w;



    // if (fDistortion > 0){
        // lowp vec3 sum = vec3(0.0);

        // sum += texture2D(samTex, blurCoordinates[0]).rgb * 0.05;
        // sum += texture2D(samTex, blurCoordinates[1]).rgb * 0.09;
        // sum += texture2D(samTex, blurCoordinates[2]).rgb * 0.12;
        // sum += texture2D(samTex, blurCoordinates[3]).rgb * 0.15;
        // sum += texture2D(samTex, blurCoordinates[4]).rgb * 0.18;
        // sum += texture2D(samTex, blurCoordinates[5]).rgb * 0.15;
        // sum += texture2D(samTex, blurCoordinates[6]).rgb * 0.12;
        // sum += texture2D(samTex, blurCoordinates[7]).rgb * 0.09;
        // sum += texture2D(samTex, blurCoordinates[8]).rgb * 0.05;

        // FragColor = vec4(sum,fragColor.a);
    // }




    if(fNgt >= 0.5){
        FragColor = FragColor.yxzw;
    }
}