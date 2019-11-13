#version 330

in vec4 fCol;
in vec2 fTex;
in float fNgt;

uniform sampler2D samTex;
out vec4 FragColor;

void main(void){
    
    FragColor = texture(samTex, fTex);
    if(fNgt > 0){
        FragColor = FragColor.yxzw;
    }
}