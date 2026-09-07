import urllib.request

headers = {'X-Actor-ID': 'emp-001', 'X-Tenant-ID': 'org-nova-01'}
for p in ['', '/attendance', '/leave', '/payslips', '/work-logs']:
    try:
        url = f'http://localhost:8000/api/v1/me{p}'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as resp:
            print(f"{p or '/'} -> {resp.status}")
    except Exception as e:
        print(f"{p or '/'} -> ERROR: {e}")
