#!/bin/bash
# Test script to check if manual data endpoint is working

echo "🔄 Testing manual data endpoint..."
echo ""

response=$(curl -s -X POST \
  https://acl-guardian-backend.onrender.com/api/manual-data/test_user_$(date +%s) \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-11-02",
    "steps": 10000,
    "distance_km": 7.5,
    "calories": 2500,
    "active_minutes": 60,
    "peak_minutes": 25,
    "resting_heart_rate": 65,
    "sleep_hours": 7.5,
    "sleep_efficiency": 85
  }')

echo "Response:"
echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
echo ""

if echo "$response" | grep -q "success"; then
  echo "✅ SUCCESS! Manual data endpoint is working!"
  exit 0
elif echo "$response" | grep -q "user_id"; then
  echo "❌ FAILED: Still has old code (user_id error)"
  echo "⏳ Wait a bit longer for Render to finish deploying..."
  exit 1
else
  echo "⚠️  UNKNOWN: Check response above"
  exit 1
fi
