"use strict";Object.defineProperty(exports, "__esModule", {value: true});

var _chunkA6MCOX76cjs = require('./chunk-A6MCOX76.cjs');
require('./chunk-OQWD4OKR.cjs');

// src/astro.ts
function astro_default(options) {
  return {
    name: "unplugin-auto-import",
    hooks: {
      "astro:config:setup": async (astro) => {
        var _a;
        (_a = astro.config.vite).plugins || (_a.plugins = []);
        astro.config.vite.plugins.push(_chunkA6MCOX76cjs.unplugin_default.vite(options));
      }
    }
  };
}


exports.default = astro_default;
