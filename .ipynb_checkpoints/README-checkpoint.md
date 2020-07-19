# COMP5703-CS70: PEP Detection

To install required dependencies:

`pip install -r requirements.txt`

To run app:

`python main.py`


# Data Introduction

After confirm requiremnts from the client, we need to collect person wearing helment, vest or lab coat data. The project needs to collect large amount of data. The data mainly contains two sources: scrape images from websites and open source data. For this project,we found and use two open source data which are GDUT-HWD and Pictorv3. The open source data contains 3995 images with 7865 positive classes and 7672 negative classes. The scrape images are mianly person wearing lab coat which contains 1073 images with 3018 positive classes and 287 negative classes.

## 1.Data Scraping 

Using Selenium and downloaded the related WebDriver to successfully download our lab coat dataset, helmet and vest images.The powerful selenium which can automate the Google browser through clicking button, scrolling pages, waiting for loading and extracting URLs.Inputting the key words for scraping is challenge, we should use 'construction worker' or 'people wearing Safety vest' instead of using only 'Safety Helmet' or 'Safety Vest'.

## 2. Data Labeling

We used the open source labeling tool labelImg. The labeling process just takes time and effort. During labeling, we also need to manually write  

```python

```
