const fs = require("fs");
const zlib = require("zlib");

compressedData = fs.readFileSync("front_compressed.csv");
decompressedData = zlib.inflateSync(compressedData);
fs.writeFileSync("front_decompressed.csv", decompressedData);

compressedData = fs.readFileSync("front_compressed.csv");
decompressedData = zlib.inflateSync(compressedData);
fs.writeFileSync("front_decompressed.csv", decompressedData);

console.log("Decompression complete!");
console.log("Compressed size:", compressedData.length, "bytes");
console.log("Decompressed size:", decompressedData.length, "bytes");
