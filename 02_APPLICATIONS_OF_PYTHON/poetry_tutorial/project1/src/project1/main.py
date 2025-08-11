# test_dependencies.py

def test_requests():
    try:
        import requests
        response = requests.get("https://httpbin.org/get")
        print("✅ requests OK:", response.status_code)
    except ImportError:
        print("❌ requests not installed")
    except Exception as e:
        print("❌ requests error:", e)

def test_numpy():
    try:
        import numpy as np
        arr = np.array([1, 2, 3])
        print("✅ numpy OK:", arr + 1)
    except ImportError:
        print("❌ numpy not installed")
    except Exception as e:
        print("❌ numpy error:", e)

def test_pandas():
    try:
        import pandas as pd
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        print("✅ pandas OK:\n", df)
    except ImportError:
        print("❌ pandas not installed")
    except Exception as e:
        print("❌ pandas error:", e)

def test_urllib3():
    try:
        import urllib3
        http = urllib3.PoolManager()
        r = http.request("GET", "https://httpbin.org/get")
        print("✅ urllib3 OK:", r.status)
    except ImportError:
        print("❌ urllib3 not installed")
    except Exception as e:
        print("❌ urllib3 error:", e)

if __name__ == "__main__":
    test_requests()
    test_numpy()
    test_pandas()
    test_urllib3()