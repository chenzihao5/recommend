"""
@author: chenzihao
@time: 2019/11/14 下午12:04
"""
import random
import sys


class Common(object):
    @staticmethod
    def load_file(file_name):
        """load file"""
        file_open = open(file_name, 'r')
        for i, line in enumerate(file_open):
            if i == 0:
                continue
            yield line.strip('\r\n')
            if i % 100000 == 0:
                print("loading %s(%s)" % (file_name, i))
        file_open.close()
        print("load %s successfully" % file_name, file=sys.stderr)

    def split_data(self, file_name, M, k, seed, train_set, test_set):
        """split data into test set and train set"""
        train_size = 0
        test_size = 0
        random.seed(seed)
        for line in self.load_file(file_name):
            user_id, movie_id, rating, timestamp = line.split(',')
            if random.randint(0, M) == k:
                test_set.setdefault(user_id, {})
                test_set[user_id][movie_id] = float(rating)
                test_size += 1
            else:
                train_set.setdefault(user_id, {})
                train_set[user_id][movie_id] = float(rating)
                train_size += 1
        print("split train set and test set successfully", file=sys.stderr)
        print("train set size is %s" % train_size, file=sys.stderr)
        print("test set size is %s" % test_size, file=sys.stderr)
