import { defineConfig } from "astro/config";
import node from "@astrojs/node";
import tailwind from "@astrojs/tailwind";

export default defineConfig({
  output: "server",
  adapter: node({ mode: "standalone" }),
  integrations: [tailwind({ applyBaseStyles: false })],
  server: { port: 4367, host: "0.0.0.0", allowedHosts: true },
  security: { checkOrigin: false },
});
