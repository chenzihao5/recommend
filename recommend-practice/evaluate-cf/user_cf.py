"""
@author: chenzihao
@time: 2019/11/14 上午11:59
"""
import os
import sys

from common_util import Common


def cal_average(movies):
    sum = 0
    count = 0
    for movie, score in movies.items():
        sum += score
        count += 1
    return sum / (1.0 * count)


def cal_sim(movies, movies_1, average, average_1):
    """pearson correlation coefficient"""
    for movie, score in movies.items():
        if movie not in movies_1.keys():
            movies_1[movie] = average_1
    for movie, score in movies_1.items():
        if movie not in movies.keys():
            movies[movie] = average
    xy_res = 0
    xx_res = 0
    yy_res = 0
    for movie in movies.keys():
        xy_res += (movies[movie] - average) * (movies_1[movie] - average_1)
        xx_res += (movies[movie] - average) ** 2
        yy_res += (movies_1[movie] - average_1) ** 2
    if xx_res * yy_res == 0:
        return 0
    return xy_res / (xx_res * yy_res)


class UserCF(object):
    test_set = {}
    train_set = {}

    user_sim_matrix = {}

    def split_data(self, file, M, k, seed):
        Common().split_data(file, M, k, seed, self.train_set, self.test_set)

    def user_sim(self):
        """calculate the similarity between everyone"""
        for user, movies in self.train_set.items():
            if user not in self.user_sim_matrix:
                self.user_sim_matrix.setdefault(user, {})
            average = cal_average(movies)
            for user_1, movies_1 in self.train_set.items():
                if user == user_1:
                    continue
                elif user_1 in self.user_sim_matrix.keys():
                    self.user_sim_matrix[user][user_1] = self.user_sim_matrix[user_1][user]
                    print("calculate the similarity of %s and %s successfully" % (user, user_1), file=sys.stderr)
                else:
                    average_1 = cal_average(movies_1)
                    self.user_sim_matrix[user][user_1] = cal_sim(movies, movies_1, average, average_1)
                    print("calculate the similarity of %s and %s successfully" % (user, user_1), file=sys.stderr)

    def recommend(self):



if __name__ == "__main__":
    rating_file = os.path.join("..", "resource", "ml-latest-small", "ratings.csv")
    user_cf = UserCF()
    my_M = 8
    my_k = 0
    my_seed = 0
    # 每次实验选取不同的k(0≤k≤M-1)和相同的随机数种子seed，进行M次实验就可以得到M个不同的训练集和测试集，分别进行实验取平均值
    user_cf.split_data(rating_file, my_M, my_k, my_seed)
    user_cf.user_sim()
    print(user_cf.user_sim_matrix)