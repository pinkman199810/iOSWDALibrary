### how to use iOSWDALibrary
- Installed the WDA in your iOS device
- Forward the device WDA port(default:8100) on localhost:prot
    - Tidevice
    - iProxy
- Example code:
```python
import iOSWDALibrary

lib = iOSWDALibrary()
lib.temp_wda_session(wda_url='http://127.0.0.1:8100', bundle_ID='com.daimler.ris.mercedesme.cn.ios.stage')
lib.wait_until_page_contains("EQS 480", timeout="10s")
```
- If you want to get more function, please review:[iOSWDALibrary.html](iOSWDALibrary.html)