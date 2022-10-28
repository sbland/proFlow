const resolve = require("@rollup/plugin-node-resolve");
const commonjs = require("@rollup/plugin-commonjs");
const typescript = require("@rollup/plugin-typescript");
const { terser } = require("rollup-plugin-terser");
const html = require("@rollup/plugin-html");
const packageJson = require("./package.json");

module.exports = {
  input: "src/index.ts",
  output: [
    {
      file: packageJson.main,
      format: "cjs",
      sourcemap: false,
      name: "proflow-gui",
    },
    {
      file: packageJson.module,
      format: "esm",
      sourcemap: true,
    },
    {
      file: "dist/web/index.js",
      format: "iife",
      name: "proflowgui",
    },
    {
      file: "../../proflow/analysis/webview/static/force/index.js",
      format: "iife",
      name: "proflowgui",
    },

  ],
  plugins: [
    resolve(),
    commonjs(),
    // html(),
    typescript({ tsconfig: "./tsconfig.json" }),
    terser(),
  ],
};
