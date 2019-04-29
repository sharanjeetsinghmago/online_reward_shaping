#version 330
in vec2 texCoords;
out vec4 FragColor;
uniform sampler2D terrainTexture;

void main()
{    
    FragColor = texture(terrainTexture, texCoords);
    FragColor = vec4(1.0, 1.0, 1.0, 1.0);
}
