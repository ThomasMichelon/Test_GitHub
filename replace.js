const replace = require("replace-in-file");
const volumeDir = "/home/nabla/tmp";

// Interpolate the configuration of OpenFoam with the ENV
// variables provided.
const from = [/{{ unit }}/g, /{{ wind_speed }}/g];
const to = [process.env.UNIT, process.env.WIND_SPEED];

const options = {
  files: `${volumeDir}/OpenFoam/**/*`,
  from: from,
  to: to,
};

try {
  const results = replace.sync(options);
  const replaced = results.filter((r) => r.hasChanged === true);
  console.log("Files with replacements:");
  replaced.map((r) => console.log(r.file));
  console.log("\n");
} catch (error) {
  console.error("Error occurred: ", error);
}
