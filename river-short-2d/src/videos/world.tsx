import React from "react";
// Flat vector world (river, trestle bridge, factory, skyline, trees). Ink outlines = SVG stroke.
// All shapes live in WORLD coordinates (see story.ts); the camera transform is applied by the parent.
import { WORLD } from "../story";

const INK = "#20242b";
const sw = 7; // stroke width in world units

export const World: React.FC<{ f: number }> = ({ f }) => {
  const t = f / 30;
  const smoke = [0, 1, 2].map((i) => {
    const p = ((t * 0.25 + i / 3) % 1);
    return { cx: 1760 + p * 160 + i * 30, cy: 1560 - p * 320, r: 40 + p * 90, o: 0.35 * (1 - p) };
  });
  const clouds = [0, 1, 2].map((i) => ({ cx: 300 + i * 750 + ((t * 6) % 120), cy: 300 + (i % 2) * 160 }));
  return (
    <svg width={WORLD.w} height={WORLD.h} viewBox={`0 0 ${WORLD.w} ${WORLD.h}`} style={{ display: "block" }}>
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#bfe3f2" />
          <stop offset="0.75" stopColor="#e8f3ef" />
          <stop offset="1" stopColor="#f6ecd9" />
        </linearGradient>
        <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#2b93a0" />
          <stop offset="1" stopColor="#176273" />
        </linearGradient>
      </defs>
      <rect x={0} y={0} width={WORLD.w} height={WORLD.h} fill="url(#sky)" />
      <circle cx={520} cy={420} r={150} fill="#ffd98a" stroke={INK} strokeWidth={sw} />
      {clouds.map((c, i) => (
        <g key={i} opacity={0.9}>
          <ellipse cx={c.cx} cy={c.cy} rx={150} ry={55} fill="#ffffff" stroke={INK} strokeWidth={sw * 0.7} />
          <ellipse cx={c.cx + 110} cy={c.cy + 18} rx={100} ry={42} fill="#ffffff" stroke={INK} strokeWidth={sw * 0.7} />
        </g>
      ))}
      {/* far skyline */}
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <rect key={i} x={180 + i * 330} y={1180 - (i % 3) * 120} width={220} height={900 + (i % 3) * 120}
          fill={i % 2 ? "#c9d4d8" : "#b7c6cc"} stroke={INK} strokeWidth={sw} />
      ))}
      {/* factory */}
      <g>
        <rect x={1620} y={1420} width={560} height={640} fill="#d9a066" stroke={INK} strokeWidth={sw} />
        <rect x={1660} y={1300} width={90} height={140} fill="#b8785a" stroke={INK} strokeWidth={sw} />
        <rect x={1800} y={1280} width={90} height={160} fill="#b8785a" stroke={INK} strokeWidth={sw} />
        {[0, 1, 2, 3].map((i) => (
          <rect key={i} x={1650 + i * 130} y={1500} width={80} height={110} fill="#7fb2c9" stroke={INK} strokeWidth={sw * 0.8} />
        ))}
        {smoke.map((s, i) => (
          <circle key={i} cx={s.cx} cy={s.cy} r={s.r} fill="#e8e8e8" opacity={s.o} />
        ))}
      </g>
      {/* ground banks */}
      <rect x={0} y={2060} width={WORLD.w} height={WORLD.h - 2060} fill="#8fbf6f" stroke={INK} strokeWidth={sw} />
      {/* river */}
      <path d={`M 0 2260 C 600 2180, 1100 2380, 1700 2300 C 2100 2250, 2300 2320, 2400 2300 L 2400 2900 C 1800 2980, 1200 2800, 600 2880 C 300 2920, 100 2880, 0 2900 Z`}
        fill="url(#water)" stroke={INK} strokeWidth={sw} />
      {/* oil slick sheen */}
      {[0, 1, 2, 3].map((i) => (
        <ellipse key={i} cx={500 + i * 480 + Math.sin(t * 0.7 + i) * 30} cy={2560 + (i % 2) * 90}
          rx={150 + (i % 3) * 40} ry={26} fill="#3d3a55" opacity={0.55} />
      ))}
      {/* trestle bridge */}
      <g stroke={INK} strokeWidth={sw}>
        <rect x={1380} y={1980} width={640} height={46} fill="#8a5a3b" />
        {[-17, -2, 13, 28].map((z) => (
          <g key={z}>
            <rect x={1420 + (z + 20) * 70} y={2026} width={46} height={420} fill="#6e452c" />
            <line x1={1420 + (z + 20) * 70} y1={2040} x2={1443 + (z + 20) * 70 + 160} y2={2440} strokeWidth={sw * 0.7} />
            <line x1={1466 + (z + 20) * 70} y1={2040} x2={1423 + (z + 20) * 70} y2={2440} strokeWidth={sw * 0.7} />
          </g>
        ))}
        <line x1={1380} y1={2003} x2={2020} y2={2003} strokeWidth={sw * 0.6} />
      </g>
      {/* trees */}
      {[[240, 2120], [420, 2160], [2100, 2140], [2260, 2180], [80, 2180]].map(([x, y], i) => (
        <g key={i}>
          <rect x={x - 14} y={y - 120} width={28} height={120} fill="#7a5230" stroke={INK} strokeWidth={sw * 0.7} />
          <circle cx={x} cy={y - 190} r={95 + (i % 3) * 22} fill={i % 2 ? "#5da05a" : "#6fb064"} stroke={INK} strokeWidth={sw} />
        </g>
      ))}
      {/* foreground bushes */}
      {[[150, 2980], [700, 3020], [1300, 3000], [1900, 3030], [2300, 2990]].map(([x, y], i) => (
        <ellipse key={i} cx={x} cy={y} rx={170} ry={90} fill="#4e8f4a" stroke={INK} strokeWidth={sw} />
      ))}
    </svg>
  );
};
