import React from "react";
import { AbsoluteFill, Composition, registerRoot, useCurrentFrame } from "remotion";

const Smoke: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#204060", alignItems: "center", justifyContent: "center" }}>
      <div style={{ color: "#fff", fontSize: 90, fontFamily: "sans-serif" }}>smoke {f}</div>
    </AbsoluteFill>
  );
};

const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Smoke" component={Smoke} durationInFrames={30} fps={30} width={1080} height={1920} />
  </>
);

registerRoot(RemotionRoot);
