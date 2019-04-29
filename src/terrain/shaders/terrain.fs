#version 330
in vec2 texCoords;
out vec4 FragColor;
uniform sampler2D terrainTexture;

void main()
{    
    vec4 Color = texture(terrainTexture, texCoords);
    FragColor = vec4(Color.rgb, 1.0);
}
