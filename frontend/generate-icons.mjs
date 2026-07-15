import sharp from "sharp";
import { mkdirSync } from "fs";

mkdirSync("public/icons", { recursive: true });

await sharp("public/logo.svg").resize(192, 192).png().toFile("public/icons/icon-192.png");
await sharp("public/logo.svg").resize(512, 512).png().toFile("public/icons/icon-512.png");

console.log("Icons generated.");
