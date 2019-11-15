## Item-CF
### 数据结构
```
    # 测试集
    test_set = {
        "user_id_1": {
            movie_id_1: score
            movie_id_2: score
            ...
        }
        ...
    }

    # 训练集
    train_set = {} //同test_set

    # 共现矩阵 次数-》相似度
    co_occur_matrix = {
        "movie_id_1": {
            “movie_id_1”: 0
            "movie_id_2": 3
            ...
        }
        ...
    }

    # 每个movie的喜欢人数统计
    movie_like_num = {
        "movie_id": 5
        ...
    }
```

### TODO
        可以对相似度进行归一化处理，可以提高覆盖度，新颖度