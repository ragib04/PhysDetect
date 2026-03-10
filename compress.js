const fs = require("fs");
const zlib = require("zlib");

binaryData = fs.readFileSync("front_angles.csv");
compressedData = zlib.deflateSync(binaryData);
fs.writeFileSync("front_compressed.csv", compressedData);

binaryData = fs.readFileSync("side_angles.csv");
compressedData = zlib.deflateSync(binaryData);
fs.writeFileSync("side_compressed.csv", compressedData);