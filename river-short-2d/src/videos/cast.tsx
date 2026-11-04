import React from "react";
// Simple 2D cutout character: deterministic walk cycle + mouth shapes driven by words.gen.json.
const INK = "#20242b";

export interface CharProps {
  x: number; y: number; scale: number; f: number; dir: 1 | -1; mouth: number; talking: boolean;
}

export const Character: React.FC<CharProps> = ({ x, y, scale, f, dir, mouth, talking }) => {
  const w = Math.sin((f / 30) * Math.PI * 2 * 1.5) * 26; // walk swing
  const bob = Math.abs(Math.sin((f / 30) * Math.PI * 3)) * 8;
  const mouthH = talking ? 6 + (mouth % 4) * 7 : 3;
  return (
    <g transform={`translate(${x},${y}) scale(${scale * dir},${scale})`}>
      {/* legs */}
      <line x1={-12} y1={-120} x2={-12 + w * 0.6} y2={0} stroke={INK} strokeWidth={16} strokeLinecap="round" />
      <line x1={12} y1={-120} x2={12 - w * 0.6} y2={0} stroke={INK} strokeWidth={16} strokeLinecap="round" />
      {/* body */}
      <rect x={-34} y={-230 + bob} width={68} height={118} rx={26} fill="#e2574c" stroke={INK} strokeWidth={7} />
      {/* arm */}
      <line x1={26} y1={-210 + bob} x2={26 - w * 0.5} y2={-140 + bob} stroke={INK} strokeWidth={13} strokeLinecap="round" />
      {/* head */}
      <circle cx={0} cy={-285 + bob} r={46} fill="#f2c9a0" stroke={INK} strokeWidth={7} />
      {/* hair */}
      <path d={`M -46 -295 a 46 46 0 0 1 92 0 l 0 -12 a 46 30 0 0 0 -92 0 Z`} fill="#4a3226" stroke={INK} strokeWidth={6} />
      {/* eyes */}
      <circle cx={-15} cy={-290 + bob} r={5.5} fill={INK} />
      <circle cx={15} cy={-290 + bob} r={5.5} fill={INK} />
      {/* mouth */}
      <ellipse cx={0} cy={-268 + bob} rx={9} ry={mouthH} fill="#7c3a2d" stroke={INK} strokeWidth={4} />
    </g>
  );
};
