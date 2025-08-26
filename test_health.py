import requests

try:
    response = requests.get('http://localhost:8000/api/health')
    if response.status_code == 200:
        health = response.json()
        print('🏥 Backend Health Check:')
        print(f'   Status: {health["status"]}')
        print(f'   Service: {health["service"]}')
        if 'data_cleaning' in health:
            dc = health['data_cleaning']
            print(f'   Cleaning Method: {dc["method"]}')
            print(f'   Efficiency: {dc["efficiency"]}') 
            print(f'   Data Loss: {dc["data_loss"]}')
            print(f'   Status: {dc["status"]}')
        print('✅ Backend integration successful!')
    else:
        print(f'❌ Backend not responding: {response.status_code}')
except:
    print('❌ Backend not running or not accessible')
