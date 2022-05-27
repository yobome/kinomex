# kinomex
A script used to upload and download on the Kinomex. (https://kinome.simm.ac.cn/en/)

# Usage
```python
from kinomex import KinomeX
k = KinomeX("YOUR_SESSIONID", "YOUR_CRSF_TOKEN")
k.upload_one("/path/to/your.txt")
k.upload_all("/path/to/your/directory")
k.download_all("/path/to/your/directory")
```
