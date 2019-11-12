"""
@author: chenzihao
@time: 2019/11/11 下午3:42
"""
import os
import sys
from collections import defaultdict
import random
from operator import itemgetter


class ItemCF(object):
    """off-line experiment of top-N recommendation by item-cf"""
    test_set = {}
    train_set = {}
    co_occur_matrix = {}
    movie_like_num = {}

    sim_movie_num = 20
    recommend_movie_num = 10

    @staticmethod
    def load_file(file_name):
        """
            load file
            return generator
        """
        file_open = open(file_name, 'r')
        for i, line in enumerate(file_open):
            if i == 0:
                continue
            yield line.strip('\r\n')
            if i % 100000 == 0:
                print("loading %s(%s)" % (file_name, i), file=sys.stderr)
        file_open.close()
        print("load %s successfully" % file_name, file=sys.stderr)

    def split_data(self, file_name, M, k, seed):
        """split data into test set and train set"""
        train_size = 0
        test_size = 0
        random.seed(seed)
        for line in self.load_file(file_name):
            user_id, movie_id, rating, timestamp = line.split(',')
            if random.randint(0, M) == k:
                self.test_set.setdefault(user_id, {})
                self.test_set[user_id][movie_id] = rating
                test_size += 1
            else:
                self.train_set.setdefault(user_id, {})
                self.train_set[user_id][movie_id] = rating
                train_size += 1
        print("split train set and test set successfully", file=sys.stderr)
        print("train set size is %s" % train_size, file=sys.stderr)
        print("test set size is %s" % test_size, file=sys.stderr)

    def movie_sim(self):
        """calculate movie similarity"""
        # build co_occur_matrix
        for user_id, movies in self.train_set.items():
            for movie_id in movies.keys():
                # calculate the total number of user who like each movie
                self.movie_like_num[movie_id] = self.movie_like_num.setdefault(movie_id, 0) + 1
                # co_occur_matrix
                self.co_occur_matrix.setdefault(movie_id, defaultdict(int))
                for movie_id_1 in movies.keys():
                    if movie_id == movie_id_1:
                        continue
                    else:
                        self.co_occur_matrix[movie_id][movie_id_1] += 1
        print("build co_occur_matrix successfully")
        # calculate similarity
        for movie_id, movies in self.co_occur_matrix.items():
            for movie_id_1, count in movies.items():
                self.co_occur_matrix[movie_id][movie_id_1] \
                    = count / (self.movie_like_num[movie_id] * self.movie_like_num[movie_id_1]) ** 0.5
        print("calculate movie similarity successfully", file=sys.stderr)
        return self.co_occur_matrix

    def recommend(self, user_id):
        """recommend N movies, top-K similar of movie"""
        rank_res = {}
        movies = self.train_set[user_id]
        for movie, rating in movies:
            for related_movie, similarity in sorted(
                    self.co_occur_matrix[movie].items(), key=itemgetter(1), reverse=True)[:self.sim_movie_num]:
                if related_movie in movies:
                    continue
                else:
                    rank_res[related_movie] += rank_res.setdefault(related_movie, 0) + similarity * rating
        return sorted(rank_res, key=itemgetter(1), reverse=True)[:self.recommend_movie_num]

    def evaluate(self):
        """print evaluate result: recall, precision, coverage, popularity"""
        hit = 0
        recall_all = 0
        precision_all = 0
        for user in self.train_set.keys():
            test_movies = self.test_set.get(user, {})
            recommend_res = self.recommend(user)
            for movie, score in recommend_res:
                if movie in test_movies:
                    hit += 1
                recall_all += len(test_movies)
        # recall
        recall = hit / (1.0 * recall_all)
        print("recall: %.4f" % recall, file=sys.stderr)


if __name__ == '__main__':
    rating_file = os.path.join('..', '..', 'resource', 'ml-20m', 'ratings.csv')
    item_cf = ItemCF()
    my_M = 8
    my_k = 0
    my_seed = 10
    # 每次实验选取不同的k(0≤k≤M-1)和相同的随机数种子seed，进行M次实验就可以得到M个不同的训练集和测试集，分别进行实验取平均值
    item_cf.split_data(rating_file, my_M, my_k, my_seed)
    item_cf.movie_sim()
    res = item_cf.co_occur_matrix
    count_num = 0
    for movie_id, movies in res.items():
        for movie_id_1, sim in movies:
            count_num += 1
            if count_num < 50:
                print(movie_id, movie_id_1, sim)
