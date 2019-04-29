#version 330
in vec2 texCoords;
out vec4 FragColor;
uniform sampler2D terrainTexture;
uniform sampler2D rewardMap;
void main()
{    
    vec4 terrainColor = texture(terrainTexture, texCoords);
    vec4 rewardColor = texture(rewardMap, texCoords);
    float alpha = 0.2*(1-rewardColor.g/255.0);
    FragColor = vec4(terrainColor.rgb, 1.0)*(1.0-alpha) + vec4(rewardColor.r, 0.0, rewardColor.b, 1.0)*alpha/255.0;
}
