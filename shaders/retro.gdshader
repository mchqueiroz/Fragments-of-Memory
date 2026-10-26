shader_type canvas_item;
// Pós-processo com três "looks" (para escolher a assinatura visual do jogo):
//   0 = atual (PS1 sombrio, cores dessaturadas)
//   1 = foto de arquivo retocada: quase monocromática; só o vermelho soviético e a luz âmbar sobrevivem,
//       e o que é "esquecido" vira papel em branco (como pessoas apagadas de fotografias oficiais)
//   2 = quatro tintas (preto-tinta, vermelho soviético, papel envelhecido, branco osso): cartaz construtivista

uniform sampler2D screen_tex : hint_screen_texture, filter_nearest;
uniform int look = 0;
uniform float levels = 6.0;
uniform float dither = 0.09;
uniform float saturation = 0.6;
uniform float exposure = 1.05;
uniform vec3 tint = vec3(1.0, 1.0, 1.0);
uniform float grain = 0.03;     // grão de filme
uniform float aberration = 0.0016; // franja de cor nas bordas (cresce com o esquecimento)
uniform float forget = 0.12; // 0 = visão inteira, 1 = só o centro: a memória se apaga pelas bordas

const mat4 BAYER = mat4(
	vec4(0.0, 8.0, 2.0, 10.0),
	vec4(12.0, 4.0, 14.0, 6.0),
	vec4(3.0, 11.0, 1.0, 9.0),
	vec4(15.0, 7.0, 13.0, 5.0));

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

// quatro tintas do look 2 (padrão: vermelho soviético = passado; azul de cianótipo = presente)
uniform vec3 ink_dark = vec3(0.045, 0.040, 0.050);
uniform vec3 ink_mid = vec3(0.34, 0.06, 0.06);
uniform vec3 ink_paper = vec3(0.66, 0.58, 0.45);
uniform vec3 ink_bone = vec3(0.93, 0.89, 0.77);

vec3 ink4(float v) {
	if (v < 0.16) return ink_dark;
	if (v < 0.34) return ink_mid;
	if (v < 0.64) return ink_paper;
	return ink_bone;
}

void fragment() {
	vec2 ab = (SCREEN_UV - 0.5) * length(SCREEN_UV - 0.5) * (aberration * 1.5 + forget * 0.008); // só nas bordas: no centro o ruído de cada canal não vira mancha colorida
	vec3 c = vec3(texture(screen_tex, SCREEN_UV + ab).r, texture(screen_tex, SCREEN_UV).g, texture(screen_tex, SCREEN_UV - ab).b);
	float lum = dot(c, vec3(0.299, 0.587, 0.114));
	ivec2 p = ivec2(FRAGCOORD.xy) % 4;
	float bayer = BAYER[p.x][p.y] / 16.0 - 0.5;
	vec3 paper = vec3(0.80, 0.75, 0.63);

	if (look == 2) {
		float redness = clamp((c.r - max(c.g, c.b)) * 2.5, 0.0, 1.0);
		float v = clamp(lum * exposure * 1.9 + bayer * 0.17, 0.0, 1.0);
		c = ink4(v);
		if (redness > 0.42 && lum > 0.08) {
			c = vec3(0.62, 0.08, 0.07) * (0.7 + lum); // objetos vermelhos "gritam"
		}
	} else {
		if (look == 1) {
			float redness = clamp((c.r - max(c.g, c.b)) * 3.0, 0.0, 1.0);
			float amber = clamp((c.r - c.b) * 1.6 - 0.25, 0.0, 1.0) * step(0.35, lum);
			vec3 gray = vec3(lum) * vec3(1.0, 0.96, 0.86);
			c = mix(gray, c * 1.15, clamp(redness * 0.9 + amber * 0.35, 0.0, 1.0));
			c = ((c - 0.45) * 1.45 + 0.45) * exposure;
		} else {
			c = mix(vec3(lum), c, saturation) * tint * exposure;
		}
		c = floor((c + bayer * dither) * levels + 0.5) / levels;
	}

	vec2 q = SCREEN_UV - 0.5;
	q.x *= 1.78;
	float edge = smoothstep(0.42 - forget * 0.3, 1.05, length(q));
	if (hash(floor(FRAGCOORD.xy / 2.0) + floor(TIME * 7.0)) < edge * forget * 2.4) {
		vec3 gone = look == 0 ? vec3(0.03, 0.03, 0.04) : paper; // nos looks 1 e 2 o esquecido vira papel em branco
		c = mix(c, gone, 0.93);
	}
	c *= smoothstep(0.95, 0.3, length(SCREEN_UV - 0.5));
	c += (hash(FRAGCOORD.xy + floor(TIME * 24.0)) - 0.5) * grain * (1.0 + forget * 2.0);
	COLOR = vec4(c, 1.0);
}
