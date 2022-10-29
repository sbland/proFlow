const resolve = require("@rollup/plugin-node-resolve");
const commonjs = require("@rollup/plugin-commonjs");
const typescript = require("@rollup/plugin-typescript");
const { terser } = require("rollup-plugin-terser");
const nodePolyfills = require("rollup-plugin-polyfill-node");

module.exports = {
  input: "src/index.ts",
  // TODO: Should package up d3js
  external: ["d3"],
  output: [
    {
      file: "dist/web/index.js",
      format: "iife",
      name: "proflowgui",
      globals: {
        d3: "d3",
      },
    },
    // TODO: Fix copying file to app dir
    // {
    //   file: "../../proflow/analysis/webview/static/force/index.js",
    //   format: "iife",
    //   name: "proflowgui",
    //   globals: {
    //     d3: "d3",
    //   },
    // },
  ],
  plugins: [
    resolve(),
    commonjs(),
    typescript({ tsconfig: "./tsconfig.json" }),
    terser(),
    nodePolyfills(),
  ],
};
