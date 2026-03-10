NOTE='\033[0;36m'
ENDNOTE='\033[0m'

echo -e "${NOTE}now we compress the frame data${ENDNOTE}"
node compress.js

echo -e "${NOTE}generating keys${ENDNOTE}"
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes
cp server.key serv_dir/server.key
cp server.crt serv_dir/server.crt


echo -e "${NOTE}open server on port 60000${ENDNOTE}"
read -p "press enter to continue"

echo -e "${NOTE}open client${ENDNOTE}"
./client 127.0.0.1 front_compressed.csv
./client 127.0.0.1 side_compressed.csv
./client 127.0.0.1 end

cd serv_dir

echo -e "${NOTE}decompress frame data${ENDNOTE}"
node decompress.js

echo -e "${NOTE}server status${ENDNOTE}"
ls
