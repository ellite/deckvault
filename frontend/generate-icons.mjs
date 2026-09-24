import sharp from "sharp";
import { mkdirSync } from "fs";

mkdirSync("public/icons", { recursive: true });

for (const size of [180, 192, 512]) {
  await sharp("public/logo.svg")
    .resize({
      width: size,
      height: size,
      fit: "contain",
      background: { r: 0, g: 0, b: 0, alpha: 0 },
    })
    .png()
    .toFile(`public/icons/icon-${size}.png`);
}

console.log("Icons generated.");
