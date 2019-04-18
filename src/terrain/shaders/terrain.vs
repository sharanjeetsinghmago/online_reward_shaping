#version 330

layout (location = 0) in vec3 aPos;

out vec2 texCoords;

uniform mat4 model;
uniform mat4 view;
uniform mat4 perspective;

uniform sampler2D heightMap;

void main()
{
    texCoords = vec2((aPos.x)/2.0 + 0.5, -(aPos.z)/2.0 + 0.5);

    vec4 Pos = vec4(aPos, 1.0);
    Pos.y = texture(heightMap, texCoords).r*0.05;
    gl_Position = perspective * view * model * Pos;
}
