# COMP5703-CS70: PEP Detection

To install required dependencies:

`pip install -r requirements.txt`

To download the below three [[checkpoint files](https://drive.google.com/drive/folders/1mOjkvQQBEcLV4ju2N9JYhDiROGwC1MHb?usp=sharing)] and place them under the checkpoint folder. 

`best_model_Epoch_75_step_29487_mAP_0.8609_loss_5.4903_lr_1e-05.data-00000-of-00001`
`best_model_Epoch_75_step_29487_mAP_0.8609_loss_5.4903_lr_1e-05.index`
`best_model_Epoch_75_step_29487_mAP_0.8609_loss_5.4903_lr_1e-05.meta`

### Use Input video for Detection 

The application works with input any videos. Demo videos are provided [[here](https://drive.google.com/drive/folders/13c1mlFCWxu7in9Aggz5OWsq_K9duW9M2?usp=sharing)].

In `eyre.py` change
```
def init_camera(self):
    self.camera = cv2.VideoCapture('path_to_video/demo_video.mp4')
```

### Use camera Stream
In `eyre.py` change
```
def init_camera(self):
    self.camera = cv2.VideoCapture(0)
```

## Finally to run the app:

`python eyre.py`



# Data Introduction

After confirm requiremnts from the client, we need to collect person wearing helment, vest or lab coat data. The project needs to collect large amount of data. The data mainly contains two sources: scrape images from websites and open source data. For this project,we found and use two open source data which are GDUT-HWD and Pictorv3. The open source data contains 3995 images with 7865 positive classes and 7672 negative classes. The scrape images are mainly person wearing lab coat which contains 1073 images with 3018 positive classes and 287 negative classes. Besides, the extracted dataset from filmed videos contains 1,437 images with 2,734 positive instances and 204 negative instances.

Training dataset can be downloaded here

`https://drive.google.com/file/d/17T_aHFxhq3BNDn2iTJASKT6HYdUoph3A/view?usp=sharing`

## 1.Data Scraping 

Using Selenium and downloaded the related WebDriver to successfully download our lab coat dataset, helmet and vest images.The powerful selenium which can automate the Google browser through clicking button, scrolling pages, waiting for loading and extracting URLs.Inputting the key words for scraping is challenge, we should use 'construction worker' or 'people wearing Safety vest' instead of using only 'Safety Helmet' or 'Safety Vest'.

You can choose key words such as "construction worker"  

Except scraping data from websites, another direct data collection method is to record videos for user scenes. 




## 2. Data Labeling

We used the open source labelling tool [[LabelImg](https://github.com/tzutalin/labelImg)]. The labelling process just takes time and effort. Referring to figure 1, our project directly label data into five classes (P, PH, PV, PHV, PLC) and then implement YOLOv3 model to classify data into different classes.
![image.png](attachment:image.png)


In order to reduce the noise from different background, we strictly labelled data from head to knees and shoulder to shoulder (figure 2). In addition, when a class is incorrectly labelled or a typo is made, we need to use the ElemetTree class in Python to process the annotation XML file for error corrections. 
![image.png](attachment:image.png)

#  PPE Detection Model Training Tutorial


### 1. Requirements

Python version: 3.7

Packages:

- tensorflow < 2 (theoretically any version that supports tf.data is ok)
- opencv-python
- tqdm

### 2. Weights download

You need download the converted TensorFlow checkpoint file by me via [[Google Drive link](https://drive.google.com/drive/folders/1mXbNgNxyXPi7JNsnBaxEv1-nWr7SVoQt?usp=sharing)] or [[Github Release](https://github.com/wizyoung/YOLOv3_TensorFlow/releases/)] and then place it to the `./data/darknet_weights/` directory.


### 3. Training

#### 3.1 Data preparation

Put the VOC format dataset in `./data/mydata/` directory.

(1) annotation file

Run `python data_pro.py` to generate `train.txt/val.txt/test.txt` files under `./data/my_data/` directory. One line for one image, in the format like `image_index image_absolute_path img_width img_height box_1 box_2 ... box_n`. Box_x format: `label_index x_min y_min x_max y_max`. (The origin of coordinates is at the left top corner, left top => (xmin, ymin), right bottom => (xmax, ymax).) `image_index` is the line index which starts from zero. `label_index` is in range [0, class_num - 1].

For example:

```
0 xxx/xxx/a.jpg 1920 1080 0 453 369 473 391 1 588 245 608 268
1 xxx/xxx/b.jpg 1920 1080 1 466 403 485 422 2 793 300 809 320
...
```

(2)  class_names file:

`coco.names` file under `./data/my_data/` directory. Each line represents a class name.

```
P
PH
PV
PHV
PLC
...
```

(3) prior anchor file:

Using the kmeans algorithm to get the prior anchors:

```
python get_kmeans.py
```

Then you will get 9 anchors and the average IoU. Save the anchors to `./data/yolo_anchors.txt`

The yolo anchors computed by the kmeans script is on the resized image scale.  The default resize method is the letterbox resize, i.e., keep the original aspect ratio in the resized image.

#### 3.2 Training

Using `train.py`. The hyper-parameters and the corresponding annotations can be found in `args.py`:

```shell
CUDA_VISIBLE_DEVICES=GPU_ID python train.py
```

Check the `args.py` for more details. You should set the parameters yourself in your own specific task.

Our training enviroment was:

- Ubuntu 16.04
- NVIDIA Tesla P100

### 4. Testing

You could test by running those command:

Single image test :

```shell
python test_single_image.py ./data/demo_data/test.jpg
```

Video test:

```shell
python video_test.py ./data/demo_data/test.mp4
```

# Installing dependencies on Jetson Nano

Run following scripts after setting up the Jetson Nano. Following scripts will install required dependencies

### 1. Uninstall unused applications to save space (Optional)
```
sudo apt remove libreoffice*  thunderbird shotwell rhythmbox cheese
sudo apt autoremove
```
### 2. update system
```
sudo apt-get update
```
Install dependencies
```
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3 \
    python3-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev
```
### 3. install the correct Cython version
```
python3 -m pip install Cython==0.29.10
sudo apt-get update
```
### 4. prerequisite for Tensorflow
```
sudo apt-get install libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev liblapack-dev libblas-dev gfortran
```
### 5. TensorFlow
```
python3 -m pip install --upgrade --user pip setuptools virtualenv

sudo pip3 install --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v44 'tensorflow<2'

sudo pip3 install numba
sudo pip3 install scikit-learn
sudo apt-get install python3-matplotlib
sudo pip3 install filterpy
```
