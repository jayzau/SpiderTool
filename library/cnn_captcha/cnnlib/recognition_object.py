# -*- coding: utf-8 -*-
"""
识别图像的类，为了快速进行多次识别可以调用此类下面的方法：
R = Recognizer(image_height, image_width, max_captcha)
for i in range(10):
    r_img = Image.open(str(i) + ".jpg")
    t = R.rec_image(r_img)
简单的图片每张基本上可以达到毫秒级的识别速度
"""
import tensorflow as tf
import numpy as np

from library.cnn_captcha.cnnlib.network import CNN


class Recognizer(CNN):
    def __init__(self, image_height, image_width, max_captcha, char_set, model_save_dir, model_save_name):
        # 初始化变量
        super(Recognizer, self).__init__(image_height, image_width, max_captcha, char_set, model_save_dir,
                                         model_save_name)

        # 新建图和会话
        self.g = tf.Graph()
        self.sess = tf.Session(graph=self.g)
        # 使用指定的图和会话
        with self.g.as_default():
            # 迭代循环前，写出所有用到的张量的计算表达式，如果写在循环中，会发生内存泄漏，拖慢识别的速度
            # tf初始化占位符
            self.X = tf.placeholder(tf.float32, [None, self.image_height * self.image_width])  # 特征向量
            self.Y = tf.placeholder(tf.float32, [None, self.max_captcha * self.char_set_len])  # 标签
            self.keep_prob = tf.placeholder(tf.float32)  # dropout值
            # 加载网络和模型参数
            self.y_predict = self.model()
            self.predict = tf.argmax(tf.reshape(self.y_predict, [-1, self.max_captcha, self.char_set_len]), 2)
            saver = tf.train.Saver()
            with self.sess.as_default() as sess:
                saver.restore(sess, self.model_save_path)

    # def __del__(self):
    #     self.sess.close()
    #     print("session close")

    def rec_image(self, img):
        # 读取图片
        img_resize = img.resize((self.image_width, self.image_height))
        img_array = np.array(img_resize)
        test_image = self.convert2gray(img_array)
        test_image = test_image.flatten() / 255
        # 使用指定的图和会话
        with self.g.as_default():
            with self.sess.as_default() as sess:
                text_list = sess.run(self.predict, feed_dict={self.X: [test_image], self.keep_prob: 1.})

        # 获取结果
        predict_text = text_list[0].tolist()
        p_text = ""
        for p in predict_text:
            p_text += str(self.char_set[p])

        # 返回识别结果
        return p_text


if __name__ == '__main__':
    pass
