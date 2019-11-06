#version 330
in vec3 vPos;
in vec2 vTex;
uniform mat4 modelView;
uniform mat4 projection;

out vec4 fCol;
out vec2 fTex;

void main(void){
    gl_Position = vec4(vPos.xyz, 1.0);
    fTex = vTex;
    fCol = vec4(1.0, 1.0, 1.0, 1.0);
}