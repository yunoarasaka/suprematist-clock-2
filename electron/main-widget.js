"use strict";

// Packaged widget builds always start in frameless widget mode.
if (!process.argv.includes("--widget")) {
  process.argv.push("--widget");
}
process.env.SUPREMATIST_WIDGET = "1";

require("./main.js");
