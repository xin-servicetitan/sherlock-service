# sherlock-service


# Run the app
python3 app.py

# Test the API 
curl -X POST http://127.0.0.1:5000/insert-build-details -H "Content-Type: application/json" -d "{\"build_id\": 4116731}"
