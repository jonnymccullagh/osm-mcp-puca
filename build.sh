docker build -t osm-mcp-puca:0.1 .

docker run --env-file .env -p 8000:8000 osm-mcp-puca

docker tag osm-mcp-puca:0.1 redbranch/osm-mcp-puca:0.1
docker push redbranch/osm-mcp-puca:0.1


