const fs = require("fs");
const zlib = require("zlib");

// STEP 1: Read compressed file
const compressedData = fs.readFileSync("angles_compressed.csv");

// STEP 2: Decompress
const decompressedData = zlib.inflateSync(compressedData);

// STEP 3: Save decompressed output
fs.writeFileSync("angles_decompressed.csv", decompressedData);

console.log("Decompression complete!");
console.log("Compressed size:", compressedData.length, "bytes");
console.log("Decompressed size:", decompressedData.length, "bytes");
