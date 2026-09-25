import { defineConfig } from "vite";

export default defineConfig({
  base: "./",
  // The deferred engine is ~140 KiB compressed. Enforce total transfer size
  // separately in check-budget.mjs instead of splitting it into more requests.
  build: { target: "es2022", assetsInlineLimit: 0, chunkSizeWarningLimit: 600 },
});
