import React from "react";
import { Composition } from "remotion";
import { RiverShort, RIVER_FRAMES } from "./videos/River";

export const RemotionRoot: React.FC = () => (
  <>
    {/* CPU/sandbox build: 1080x1920, no MSAA (swiftshader) — mux.sh upscales to 1440x2560 */}
    <Composition
      id="RiverShort"
      component={() => <RiverShort msaa={0} w={1080} h={1920} />}
      durationInFrames={RIVER_FRAMES}
      fps={30}
      width={1080}
      height={1920}
    />
    {/* GPU build: native 2K 1440x2560 with MSAA 4 — crisp final render, no upscale */}
    <Composition
      id="RiverShort2K"
      component={() => <RiverShort msaa={4} w={1440} h={2560} />}
      durationInFrames={RIVER_FRAMES}
      fps={30}
      width={1440}
      height={2560}
    />
  </>
);
