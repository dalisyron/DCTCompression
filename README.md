# DCTCompression
An image compression program written in python. This program uses Discrete Cosine Transform (DCT) and Quantization to reduce the image size. The algorithm is generally able to reduce image sizes by factor of 2-5. The program's GUI is implemented using tkinter. Threading was used to assure the program is responsive even while the image compression computation is performed.
![Preview](https://user-images.githubusercontent.com/34644374/136184529-1d691aad-86de-41d5-8759-8bef276fb2ec.png)

# Usage
You need Python 3.6+ to run the program. First make sure you have all the requirements installed:
```
pip install -r requirements.txt
```

To run the program program use:
```
python main.py
```

You can then use the GUI to select and compress your image:
![Usage](https://user-images.githubusercontent.com/34644374/136184892-5f40b1f9-5e62-4fc9-ac00-e41844dc9f8f.png)

# Implementation
A discrete cosine transform (DCT) expresses a finite sequence of data points in terms of a sum of cosine functions oscillating at different frequencies. This is especially helpful in image compression because the human eye doesn’t sense the high frequency components that well. So we can use quantization to reduce or remove those changes without any noticable changes.
![image](https://user-images.githubusercontent.com/34644374/136185645-10fdaaff-0204-4fe9-8a71-71b520dfd7ce.png)
