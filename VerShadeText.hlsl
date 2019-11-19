#version 330
in vec3 vPos;
in vec2 vTex;

uniform float vNtg;
uniform mat4 modelView;

out vec4 fCol;
out vec2 fTex;
out float fNgt;

void main(void){
    gl_Position = modelView * vec4(vPos.xyz, 1.0);
    fTex = vTex;
    fCol = vec4(1.0, 1.0, 1.0, 1.0);
    fNgt = vNtg;
}