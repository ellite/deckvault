// Run once: node generate-icons.mjs
// Requires: npm install -g sharp  OR  uses the sharp already in deps
import { readFileSync, writeFileSync } from "fs";
import { createCanvas } from "canvas";

// Fallback: create simple colored PNG icons if sharp/canvas not available
function createSimplePNG(size) {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext("2d");

  // Background
  const grad = ctx.createLinearGradient(0, 0, size, size);
  grad.addColorStop(0, "#6366f1");
  grad.addColorStop(1, "#8b5cf6");

  const r = size * 0.22;
  ctx.beginPath();
  ctx.moveTo(r, 0);
  ctx.lineTo(size - r, 0);
  ctx.quadraticCurveTo(size, 0, size, r);
  ctx.lineTo(size, size - r);
  ctx.quadraticCurveTo(size, size, size - r, size);
  ctx.lineTo(r, size);
  ctx.quadraticCurveTo(0, size, 0, size - r);
  ctx.lineTo(0, r);
  ctx.quadraticCurveTo(0, 0, r, 0);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  // D letter
  ctx.fillStyle = "white";
  ctx.font = `bold ${size * 0.45}px sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("D", size / 2, size / 2);

  return canvas.toBuffer("image/png");
}

try {
  writeFileSync("public/icons/icon-192.png", createSimplePNG(192));
  writeFileSync("public/icons/icon-512.png", createSimplePNG(512));
  console.log("Icons generated.");
} catch (e) {
  console.warn("canvas not available, skipping PNG icon generation:", e.message);
  console.warn("SVG icons will be used instead (works in modern browsers).");
}
