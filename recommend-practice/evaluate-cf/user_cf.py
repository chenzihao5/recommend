"""
@author: chenzihao
@time: 2019/11/14 上午11:59
"""
import copy
import math
import os
import sys
from operator import itemgetter

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
    movies_keys = movies.keys()
    movies_keys_1 = movies_1.keys()
    if not movies_keys & movies_keys_1:
        return 0
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
    movie_popular_set = {}

    user_sim_matrix = {}
    item_users = {}

    sim_user_num = 20
    recommend_movie_num = 10

    def split_data(self, file, M, k, seed):
        Common().split_data(file, M, k, seed, self.train_set, self.test_set)

    def user_sim(self):
        """calculate the similarity between everyone"""
        for user, movies in self.train_set.items():
            for movie in movies:
                # generate item-users
                if movie not in self.item_users:
                    self.item_users.setdefault(movie, set())
                    self.item_users[movie].add(user)
                else:
                    self.item_users[movie].add(user)
                # calculate movie popularity
                if movie not in self.movie_popular_set:
                    self.movie_popular_set[movie] = 0
                else:
                    self.movie_popular_set[movie] += 1
            # similarity
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
                    self.user_sim_matrix[user][user_1] = cal_sim(copy.deepcopy(movies), copy.deepcopy(movies_1), average, average_1)
                    print("calculate the similarity of %s and %s successfully" % (user, user_1), file=sys.stderr)

    def recommend(self, user_id):
        """recommend N movies, top-K similar of users"""
        rank_res = {}
        for related_user, similarity in sorted(
                self.user_sim_matrix[user_id].items(), key=itemgetter(1), reverse=True)[:self.sim_user_num]:
            for movie_id, score in self.train_set[related_user].items():
                if movie_id in self.train_set[user_id].keys():
                    continue
                else:
                    rank_res.setdefault(movie_id, 0)
                    rank_res[movie_id] += similarity * score
        return sorted(rank_res.items(), key=itemgetter(1), reverse=True)[:self.recommend_movie_num]

    def evaluate(self):
        hit = 0
        recall_all = 0  # sum of recall movies, for recall
        recommend_all = 0  # sum of recommended movies, for precision
        popularity_all = 0
        recommend_set = set()  # all recommend set, for coverage
        for user in self.train_set.keys():
            test_movies = self.test_set.get(user, {})
            recommend_res = self.recommend(user)
            print("get recommended result of user: %s successfully" % user, file=sys.stderr)
            for movie, score in recommend_res:
                popularity_all += math.log(1 + self.movie_popular_set[movie])
                recommend_set.add(movie)
                recommend_all += 1
                if movie in test_movies:
                    hit += 1
            recall_all += len(test_movies)
        # recall
        recall = hit / (1.0 * recall_all)
        # precision
        precision = hit / (1.0 * recommend_all)
        # coverage
        coverage = len(recommend_set) / (1.0 * len(self.movie_popular_set))
        # popularity
        popularity = popularity_all / (1.0 * recommend_all)

        print("recall: %.5f\nprecision: %.5f\ncoverage: %.5f\npopularity: %.5f"
              % (recall, precision, coverage, popularity), file=sys.stderr)


if __name__ == "__main__":
    rating_file = os.path.join("..", "resource", "ml-latest-small", "ratings.csv")
    user_cf = UserCF()
    my_M = 8
    my_k = 0
    my_seed = 0
    # 每次实验选取不同的k(0≤k≤M-1)和相同的随机数种子seed，进行M次实验就可以得到M个不同的训练集和测试集，分别进行实验取平均值
    user_cf.split_data(rating_file, my_M, my_k, my_seed)
    user_cf.user_sim()
    user_cf.evaluate()
