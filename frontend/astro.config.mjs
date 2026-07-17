import { defineConfig } from "astro/config";
import node from "@astrojs/node";
import svelte from "@astrojs/svelte";
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  integrations: [svelte(), tailwind({ applyBaseStyles: false })],
  server: { port: 4367, host: "0.0.0.0" },
  security: { checkOrigin: true },
});
