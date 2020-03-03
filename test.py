# 
import pandas as pd
# def name(i):
#     return 'data/' + str(i) + 'unittime.csv'
# df1 = pd.read_csv(name(1))
# df2 = pd.read_csv(name(2))
# data = {}
# # df = pd.concat([df1, df2], axis=1, join='inner')
# # print(df)
# for i in range(1,31):
#     tmp = pd.read_csv(name(i))
#     data[i] = [item[0] for item in tmp.values]
#     print(data[i])
#     # df = pd.concat([df, tmp], axis=1, join='inner')
# df = pd.DataFrame(data=data)
# print(df)
# df.columns = [i for i in range(1,31)]
# df.to_csv('test.csv',index=False)

import networkx as nx
import igraph
import pylab
import random

import igraph

# 创建一个空对象
g = igraph.Graph()
# 添加网络中的点
vertex = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
g.add_vertices(vertex)
# 添加网络中的边
edges = [('a', 'c'), ('a', 'e'), ('a', 'b'), ('b', 'd'), ('b', 'g'), ('c', 'e'),
         ('d', 'f'), ('d', 'g'), ('e', 'f'), ('e', 'g'), ('f', 'g')]
g.add_edges(edges)
# -----------------------其它信息-----------------------------
# 国家名称
g.vs['label'] = ['齐', '楚', '燕', '韩', '赵', '魏', '秦']
# 国家大致相对面积（为方便显示没有采用真实面积）
g.vs['aera'] = [50, 100, 70, 40, 60, 40, 80]
# 统计日期
g['Date'] = '公元前279年'
# -----------------------简单作图-----------------------------
# 选择图的布局方式
layout = g.layout('kk')
# 用Igraph内置函数绘图
# -----------------------设置参数-----------------------------
# 参数集合。visual_style是一个参数字典，可以动态添加想要个性化设定的参数


# ---------------------给边设定颜色---------------------------
# 默认为黑色
edge_color = dict(zip(edges, ['black']*11))
# 最短路径里的边映射为红色。映射时需要考虑元组中对象顺序，这里按字母从小到大排序
for i in np.arange(np.size(path)-1):
    if path[i] < path[i+1]:
        edge_color[(path[i], path[i + 1])] = 'red'
    else:
        edge_color[(path[i + 1], path[i])] = 'red'
visual_style['edge_color'] = [edge_color[edge] for edge in edges]