#!/bin/bash
# Script to add Tempo datasource to Grafana via API after Grafana is running
# This works around Grafana 12.3.0 provisioning validation issue

GRAFANA_URL="${GRAFANA_URL:-http://localhost:3100}"
GRAFANA_USER="${GRAFANA_USER:-admin}"
GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-admin}"

echo "Waiting for Grafana to be ready..."
for i in {1..30}; do
    if curl -s -f "${GRAFANA_URL}/api/health" > /dev/null; then
        echo "Grafana is ready!"
        break
    fi
    echo "Waiting for Grafana... ($i/30)"
    sleep 2
done

echo "Adding Tempo datasource..."
curl -X POST \
  -H "Content-Type: application/json" \
  -u "${GRAFANA_USER}:${GRAFANA_PASSWORD}" \
  -d '{
    "name": "Tempo",
    "type": "tempo",
    "access": "proxy",
    "url": "http://tempo:3200",
    "uid": "tempo",
    "isDefault": false,
    "editable": true,
    "jsonData": {
      "search": {
        "hide": false
      },
      "nodeGraph": {
        "enabled": true
      }
    }
  }' \
  "${GRAFANA_URL}/api/datasources" 2>/dev/null | jq '.' || echo "Tempo datasource may already exist or there was an error"

echo "Adding Loki datasource..."
curl -X POST \
  -H "Content-Type: application/json" \
  -u "${GRAFANA_USER}:${GRAFANA_PASSWORD}" \
  -d '{
    "name": "Loki",
    "type": "loki",
    "access": "proxy",
    "url": "http://loki:3100",
    "uid": "loki",
    "isDefault": false,
    "editable": true,
    "jsonData": {
      "maxLines": 1000
    }
  }' \
  "${GRAFANA_URL}/api/datasources" 2>/dev/null | jq '.' || echo "Loki datasource may already exist or there was an error"

echo "Done! Datasources should now be available in Grafana."



