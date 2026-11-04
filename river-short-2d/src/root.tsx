import React from "react";
import { Composition } from "remotion";
import { Scene } from "./videos/Scene";
import { TOTAL } from "./story";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Short2D" component={Scene} durationInFrames={TOTAL} fps={30} width={1080} height={1920} />
    <Composition id="Short2DX2" component={Scene} durationInFrames={TOTAL} fps={30} width={1440} height={2560} />
  </>
);
