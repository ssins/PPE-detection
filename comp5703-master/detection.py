from __future__ import division, print_function

import tensorflow as tf
import numpy as np
import argparse
import cv2
import time
import asyncio

from utils.misc_utils import parse_anchors, read_class_names
from utils.nms_utils import gpu_nms
from utils.plot_utils import get_color_table, plot_one_box
from utils.data_aug import letterbox_resize


from model import yolov3
from sort import *

# Re-allocate the GPU memory
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.9
config.gpu_options.allow_growth = True


def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])


class DetectionService:
    def __init__(self):

        self.counter = 0  # number of people
        self.violation = 0  # number of violations

        # The path of the anchor txt file.
        anchor_path = "./data/yolo_anchors.txt"
        # Resize the input image with `new_size`, size format: [width, height]
        self.new_size = [416, 416]
        # Whether to use the letterbox resize.
        self.letterbox_resizes = True
        # The path of the class names
        class_name_path = "./data/coco.names"
        # The path of the weights to restore
        restore_path = "./checkpoint/best_model_Epoch_75_step_29487_mAP_0.8609_loss_5.4903_lr_1e-05"
        # Whether to save the video detection results.
        self.save_video = True

        self.anchors = parse_anchors(anchor_path)

        self.classes = read_class_names(class_name_path)

        self.num_class = len(self.classes)

        self.color_table = get_color_table(
            self.num_class)  # color for each label

        self.tracker = Sort()
        self.memory = {}

        self.COLORS = np.random.randint(0, 255, size=(
            200, 3), dtype="uint8")  # tracker color

        self.sess = tf.Session()
        self.input_data = tf.compat.v1.placeholder(
            tf.float32, [1, self.new_size[1], self.new_size[0], 3], name='input_data')
        yolo_model = yolov3(self.num_class, self.anchors)
        with tf.compat.v1.variable_scope('yolov3'):
            pred_feature_maps = yolo_model.forward(self.input_data, False)

        pred_boxes, pred_confs, pred_probs = yolo_model.predict(pred_feature_maps)

        pred_scores = pred_confs * pred_probs

        self.boxes, self.scores, self.labels = gpu_nms(pred_boxes,
                                                       pred_scores,
                                                       self.num_class,
                                                       max_boxes=200,
                                                       score_thresh=0.6,
                                                       nms_thresh=0.01)

        saver = tf.compat.v1.train.Saver()
        saver.restore(self.sess, restore_path)

    async def detection(self, img_ori, mode, detection_marker):
        if self.letterbox_resizes:
            img, resize_ratio, dw, dh = letterbox_resize(
                img_ori, self.new_size[0], self.new_size[1])
        else:
            height_ori, width_ori = img_ori.shape[:2]
            img = cv2.resize(img_ori, tuple(self.new_size))

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.asarray(img, np.float32)
        img = img[np.newaxis, :] / 255.
        start = time.time()
        boxes_, scores_, labels_ = self.sess.run([self.boxes, self.scores, self.labels],
                                                 feed_dict={self.input_data: img})
        end = time.time()
        print(end-start)
        # rescale the coordinates to the original image
        if self.letterbox_resizes:
            boxes_[:, [0, 2]] = (boxes_[:, [0, 2]] - dw) / resize_ratio
            boxes_[:, [1, 3]] = (boxes_[:, [1, 3]] - dh) / resize_ratio
        else:
            boxes_[:, [0, 2]] *= (width_ori/float(self.new_size[0]))
            boxes_[:, [1, 3]] *= (height_ori/float(self.new_size[1]))

        # sort -- tracker for each person
        dets = []
        if len(boxes_) > 0:

            for i in range(len(boxes_)):
                x, y, w, h = boxes_[i]

                dets.append([x, y, x+w, y+h, scores_[i]])

        # np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
        dets = np.asarray(dets)
        tracks = self.tracker.update(dets)

        new_boxes = []
        indexIDs = []

        previous = self.memory.copy()
        self.memory = {}

        for track in tracks:
            new_boxes.append([track[0], track[1], track[2], track[3]])
            indexIDs.append(int(track[4]))
            self.memory[indexIDs[-1]] = new_boxes[-1]

        if len(new_boxes) > 0:
            i = 0

            for box in new_boxes:
                x = int(box[0])
                y = int(box[1])
                w = int(box[2])
                h = int(box[3])

                color = [int(c)
                         for c in self.COLORS[indexIDs[i] % len(self.COLORS)]]

                if indexIDs[i] in previous:
                    previous_box = previous[indexIDs[i]]
                    (x2, y2) = (int(previous_box[0]), int(previous_box[1]))
                    (w2, h2) = (int(previous_box[2]), int(previous_box[3]))
                    p0 = (int(x +10), int(y +100))
                    p1 = (int(x2 +10), int(y2 + 100))
                    cv2.line(img_ori, p0, p1, color, 3) # tracker line

                    if intersect(p0, p1, (detection_marker.X1, detection_marker.Y1), (detection_marker.X2, detection_marker.Y2)):
                        self.counter += 1
                        if mode == 'PH':
                            if self.classes[labels_[i]] == 'PHV' or self.classes[labels_[i]] == 'PH':
                                pass
                            else:
                                self.violation += 1
                        elif mode == 'PV':
                            if self.classes[labels_[i]] == 'PHV' or self.classes[labels_[i]] == 'PV':
                                pass
                            else:
                                self.violation += 1
                        elif self.classes[labels_[i]] != mode:
                            self.violation += 1

                i += 1

        cv2.line(img_ori, (detection_marker.X1, detection_marker.Y1), (detection_marker.X2, detection_marker.Y2), (0, 255, 255), 3)

        for i in range(len(boxes_)):
            x0, y0, x1, y1 = boxes_[i]
            plot_one_box(img_ori, [x0, y0, x1, y1], label=self.classes[labels_[
                         i]] + ', {:.2f}%'.format(scores_[i] * 100), color=self.color_table[labels_[i]])

            if mode == 'PH':
                if self.classes[labels_[i]] == 'PHV' or self.classes[labels_[i]] == 'PH':
                    pass
                else:
                    cv2.putText(img_ori, 'Please wear: a helmet',
                                (550, 40), 0, 1, (0, 0, 255), 2)
            elif mode == 'PV':
                if self.classes[labels_[i]] == 'PHV' or self.classes[labels_[i]] == 'PV':
                    pass
                else:
                    cv2.putText(img_ori, 'Please wear: a safety vest',
                                (550, 40), 0, 1, (0, 0, 255), 2)
            elif mode == 'PLC' and self.classes[labels_[i]] != 'PLC':
                cv2.putText(img_ori, 'Please wear: a lab coat',
                            (550, 40), 0, 1, (0, 0, 255), 2)
            elif mode == 'PHV' and self.classes[labels_[i]] != 'PHV':
                cv2.putText(img_ori, 'Please wear: a helmet and a safety vest',
                            (550, 40), 0, 1, (0, 0, 255), 2)
            elif self.classes[labels_[i]] != mode:
                cv2.putText(img_ori, 'Please wear: ' + str(mode),
                            (550, 40), 0, 1, (0, 0, 255), 2)

        # print({'TotalViolation': self.violation,'TotalPeople':self.counter})

        # cv2.putText(img_ori, mode+'  Mode', (300, 40), 0,
        #             fontScale=1, color=(0, 255, 0), thickness=2)
        # cv2.putText(img_ori, 'People Count: '+ str(self.counter), (40, 620), 0,
        #             1, (255,255,255), 2)
        # cv2.putText(img_ori, 'Violation Count: '+ str(self.violation), (40, 660), 0,
        #             1, (255,255,255), 2)

        return {'TotalViolation': self.violation, 'TotalPeople': self.counter}, img_ori

    def release(self):
        self.sess.close()


class DetectionMarker(object):
    def __init__(self, x1, y1, x2, y2):
        self.X1 = x1
        self.Y1 = y1
        self.X2 = x2
        self.Y2 = y2
