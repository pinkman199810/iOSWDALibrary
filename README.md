## How to use iOSWDALibrary
Tips:This library is smooth than appium, because it is a secondary development based on [facebook-wda](https://github.com/openatx/facebook-wda), we can use very few parameters to control iOS device.
- Installed the WDA in your iOS device
- Forward the device WDA port(default:8100) to  localhost
    - Tidevice
    - iProxy
- Example code:
```python
import iOSWDALibrary

lib = iOSWDALibrary()
lib.open_application(wda_url='http://127.0.0.1:8100', bundle_ID='com.daimler.ris.mercedesme.cn.ios.stage')
lib.wait_until_page_contains("EQS 480", timeout="10s")
lib.click_text("设置")
```
### This library also can be used to test with robotframework
- If you want to get more function, please review(you need to clone or download this repo): [iOSWDALibrary.html](iOSWDALibrary.html)

### Dependence
- [requirement.txt](requirement.txt)