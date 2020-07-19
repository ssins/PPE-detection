#  PPE Detection Model Training Tutorial


### 1. Requirements

Python version: 2 or 3

Packages:

- tensorflow >= 1.8.0 (theoretically any version that supports tf.data is ok)
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






