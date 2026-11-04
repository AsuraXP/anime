import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { WORLD, camAt, TOTAL } from "../story";
import { World } from "./world";
import { Character } from "./cast";
import wordsData from "../words.gen.json";

interface Word { w: string; t0: number; t1: number }
const WORDS = (wordsData as unknown as Word[]) ?? [];

const wordAt = (t: number) => {
  for (const wd of WORDS) if (t >= wd.t0 && t < wd.t1) return wd;
  return null;
};

export const Scene: React.FC = () => {
  const f = useCurrentFrame();
  const { width: vw, height: vh } = useVideoConfig();
  const cam = camAt(f);
  const base = vw / WORLD.w; // fit world width at z=1
  const s = base * cam.z;
  const tx = vw / 2 - cam.x * s;
  const ty = vh / 2 - cam.y * s;
  const t = f / 30;
  const wd = wordAt(t);
  const talking = !!wd;
  const mouth = wd ? wd.w.length % 5 : 0;
  // character walks along the near bank
  const cx = 1150 + ((f * 1.1) % 260) - 130;
  const cy = 2985;
  return (
    <AbsoluteFill style={{ background: "#bfe3f2", overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: 0, top: 0,
          width: WORLD.w, height: WORLD.h,
          transform: `translate(${tx}px, ${ty}px) scale(${s}) rotate(${cam.roll}rad)`,
          transformOrigin: "0 0",
        }}
      >
        <World f={f} />
        <Character x={cx} y={cy} scale={1.15} f={f} dir={1} mouth={mouth} talking={talking} />
      </div>
      {/* grade overlay: cheap CSS color grade */}
      <AbsoluteFill style={{ pointerEvents: "none", mixBlendMode: "multiply", background: "rgba(255,244,214,0.06)" }} />
      <AbsoluteFill style={{ pointerEvents: "none", filter: "saturate(1.06) contrast(1.04)" }} />
    </AbsoluteFill>
  );
};

export { TOTAL };
