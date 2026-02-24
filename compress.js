const fs = require("fs");
const zlib = require("zlib");

// STEP 1: Read binary file
const binaryData = fs.readFileSync("angles.csv");

// STEP 2: Compress
const compressedData = zlib.deflateSync(binaryData);

// STEP 3: Save compressed output
fs.writeFileSync("angles_compressed.csv", compressedData);

console.log("Compression complete!");
console.log("Original size:", binaryData.length, "bytes");
console.log("Compressed size:", compressedData.length, "bytes");
