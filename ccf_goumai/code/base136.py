# -*- coding: utf-8 -*-
"""
@author: starry
@software: PyCharm
@file: base136.py
@time: 2020-12-16
@description：
"""

import pandas as pd
import numpy as np
import datetime
buyer=pd.read_csv("buyer.csv",encoding='gbk')
seller=pd.read_csv("seller.csv",encoding='gbk')
class solution:
    def __init__(self,seller,buyer):
        self.seller=seller
        self.buyer=buyer
        self.result=[]
        self.tem_seller=None
        self.tem_buyer=None
        self.tem1_seller=None
        self.tem1_buyer=None
        self.yixiang2value={"第一意向":'值','第二意向':'值.1','第三意向':'值.2','第四意向':'值.3','第五意向':'值.4'}
        self.SR_value=[40,30,20,10,0]
        self.CF_value=[33,27,20,13,7]
        self.tem_yixiang_index=0
        self.tem_yixiang=list(self.yixiang2value.keys())[self.tem_yixiang_index]

    def search_for_one_buyer(self,var,yixiangs,buyer_id,buyer_index):
        """
        给每一个buyer分配资源，分配的规则是意向优先，尽可能让该buyer满足更多的意向
        :param var:  SR CF
        :param yixiangs:     该buyer的意向
        :param buyer_id:     该buyer的id
        :param buyer_index: 该buyer在self.buyer的index
        :return:             不返回值，更新剩余资源和Buyer信息
        """
        buyer_tem=self.tem_buyer.copy()
        tem_seller=self.tem_seller.copy()
        number = buyer_tem.loc[buyer_index,'购买货物数量']#.values[0]
        satisfy_yixiang = [str(self.tem_yixiang_index+1)]
        for i, (yixiang, yixiang_value) in enumerate(yixiangs):
            if pd.isna(yixiang):
                continue
            if yixiang == '仓库' or yixiang == '年度':
                yixiang_value = int(yixiang_value)
            if sum(tem_seller[tem_seller[yixiang] == yixiang_value]['货物数量（张）']) > 0: ##尽可能的取出可以满足多个意向的
                tem_seller = tem_seller[tem_seller[yixiang] == yixiang_value]
                satisfy_yixiang.append(str(i + self.tem_yixiang_index+2))
        tem_seller = tem_seller.sort_values(by=['货物数量（张）'], ascending=True)
        for i in tem_seller.index:
            good_num = tem_seller.loc[i]['货物数量（张）']
            if good_num<=0:
                continue
            seller_id=tem_seller.loc[i]['卖方客户']
            good_id=tem_seller.loc[i]['货物编号']
            ware_id=tem_seller.loc[i]['仓库']

            # print(good_num)
            if good_num >= number:
                tem_seller.loc[i,'货物数量（张）'] = good_num - number
                self.tem_seller.loc[i,'货物数量（张）'] = good_num - number  ##真实的记录下来
                self.seller.loc[i,'货物数量（张）']=good_num - number
                self.result.append([buyer_id, seller_id, var, good_id, ware_id, number, '-'.join(satisfy_yixiang)])
                number = 0
                break
            else:
                self.result.append([buyer_id, seller_id, var, good_id, ware_id, good_num, '-'.join(satisfy_yixiang)])
                number = number - good_num
                tem_seller.loc[i,'货物数量（张）'] = 0  #tem_seller.loc[i]['货物数量（张）'] -good_num
                self.tem_seller.loc[i,'货物数量（张）'] =0  # self.tem_seller.loc[i]['货物数量（张）']-good_num
                self.seller.loc[i, '货物数量（张）']=0
                if number==0:
                    break
        self.tem_buyer.loc[buyer_index,'购买货物数量']=number
        self.buyer.loc[buyer_index,'购买货物数量']=number
        if number > 0 and sum(self.tem_seller['货物数量（张）']) > 0: ##如果满足最基础意向的还有剩下的，那么就继续  这两个哪怕有一个等一0，那么都不需要继续了。
            self.search_for_one_buyer(var,yixiangs,buyer_id,buyer_index)

    def getorder(self,buyer_tm,var,col1):
        """根据意向和购买数量对Buyer设定权重"""
        if var == "SR":
            weight = [40, 30, 20, 10]
            for i in range(self.tem_yixiang_index, 4):
                buyer_tm.loc[buyer_tm.index, '权值系数'] = buyer_tm.loc[buyer_tm.index, '权值系数'] + pd.notna(buyer_tm.loc[buyer_tm.index, col1[i]]).astype(int) * weight[i]
        else:
            weight = [33, 27, 20, 13, 7]
            for i in range(self.tem_yixiang_index, 5):
                buyer_tm.loc[buyer_tm.index, '权值系数'] = buyer_tm.loc[buyer_tm.index, '权值系数'] + pd.notna(
                    buyer_tm.loc[buyer_tm.index, col1[i]]).astype(int) * weight[i]
        buyer_tm.loc[buyer_tm.index, '权重'] = buyer_tm.loc[buyer_tm.index, '权值系数'] * buyer_tm.loc[buyer_tm.index, '购买货物数量']
        buyer_tm=buyer_tm.sort_values(by=['权重'],ascending=True)
        return buyer_tm


    def search_sameyixiang(self,emotions_and_good):
        """
        选择相同意向的buyer进行优先级分类
        :param emotions_and_good:
        :return:
        """
        for dis, var, sum1, _ in emotions_and_good:
            print(dis,var,sum1)
            if sum1<=0:
                continue
            thefirst = self.buyer[self.buyer[self.yixiang2value[self.tem_yixiang]] == dis][self.tem_yixiang].iloc[0]
            self.tem_buyer = self.buyer[(self.buyer[self.yixiang2value[self.tem_yixiang]] == dis) & (self.buyer['品种'] == var)]
            if thefirst=='年度' or thefirst=='仓库':
                dis=int(dis)
            self.tem_seller=self.seller[(self.seller[thefirst]==dis) & (self.seller['品种']==var)]  ##取出这个品种下这个意向的所有seller
            print('第几意向:', str(self.tem_yixiang_index + 1), '该意向下Buyer数量:', len(self.tem_buyer), "seller数量:",
                  len(self.tem_seller), '买方的总数量:', sum(self.tem_buyer['购买货物数量']), '卖方总数量:',
                  sum(self.tem_seller['货物数量（张）']))

            if sum(self.tem_seller['货物数量（张）'])==0:  #如果满足这个意向的货物没有了，那么就不需要了
                continue
            self.tem_buyer.loc[self.tem_buyer.index, '权值系数'] = 0

            if self.tem_yixiang_index==0 and sum(self.tem_seller['货物数量（张）'])<sum(self.tem_buyer['购买货物数量']): ##只要在是第一意向并且卖的货物少于买的货物的时候才会这
                self.tem_buyer=self.tem_buyer.sort_values(by=['平均持仓时间','购买货物数量'],ascending=False) ##根据平均持仓时间倒序，持仓时间越长的越优先挑选货物
                ##我只要把持有时间长的都弄为第一意向就可以了，别的人就不管他了。
                sum_seller= sum(self.tem_seller['货物数量（张）']) ##总共有这么多
                for ii,ij in enumerate(self.tem_buyer.index):
                    if sum_seller>0:
                        sum_seller=sum_seller-self.tem_buyer.loc[ij,'购买货物数量']
                    else:
                        ##把前面哪些人供应好了就可以了，后面的可以不管
                        tem_buyer1=self.tem_buyer[:ii]
                        if sum(tem_buyer1['购买货物数量'])>sum(self.tem_seller['货物数量（张）']): ##这么多的已经足够消化了
                            print('1111')
                        tem_buyer2=self.tem_buyer[ii:ii+1]
                        tem_buyer3=self.tem_buyer[ii+1:]
                        break
                tem_buyer1=self.getorder(tem_buyer1,var,list(self.yixiang2value.keys()).copy())
                tem_buyer3 = self.getorder(tem_buyer3, var, list(self.yixiang2value.keys()).copy())
                self.tem_buyer=pd.concat([tem_buyer1,tem_buyer2,tem_buyer3])
            else:##否则按照购买数量进行排序，购买数量越多的就越优先
                self.tem_buyer=self.getorder(self.tem_buyer,var,list(self.yixiang2value.keys()).copy())

            buyer_tem_len = len(self.tem_buyer)

            for i,buyer_index in enumerate(self.tem_buyer.index):
                buyer_id=self.tem_buyer.loc[buyer_index,'买方客户']
                if i==buyer_tem_len-1:
                    print("第几个买家：",i+1,"多少买家:",buyer_tem_len ,"买家id:",buyer_id,"时间:",datetime.datetime.now(),sum(self.buyer['购买货物数量'])==sum(self.seller['货物数量（张）'])) #
                if sum(self.tem_seller['货物数量（张）']) == 0:                        ##如果满足意向的货物没有了，那么后面的都不需要再满足了。
                    break
                yixiangs=[]
                for i in range(self.tem_yixiang_index+1,len(self.yixiang2value)):
                    yixiang=list(self.yixiang2value.keys())[i]
                    yixiang_value=self.yixiang2value[yixiang]
                    yixiangs.append(yixiang)
                    yixiangs.append(yixiang_value)
                tt = self.tem_buyer[self.tem_buyer.index== buyer_index][yixiangs]
                tt = tt.values[:1].tolist()[0]
                yixiangs=[(tt[i],tt[i+1]) for i in range(0,len(tt),2)]
                self.search_for_one_buyer(var,yixiangs,buyer_id,buyer_index)
                self.tem_seller = self.tem_seller [self.tem_seller ['货物数量（张）'] > 0]
                if i==buyer_tem_len-1:
                    print("该意向下还剩下多少卖家：",len(self.tem_seller))
            self.seller=self.seller[self.seller['货物数量（张）']>0]
            self.buyer=self.buyer[self.buyer['购买货物数量']>0]
            print("目前剩下多少买家：",len(self.buyer))
            print("目前剩下多少卖家：",len(self.seller))

    def search_by_noyixiang_onebuy(self,buyer_id,var,buyer_index):
        """
        与search_for_one_buyer相似，只是不需要在乎意向。
        :param buyer_id:
        :param var:
        :param buyer_index:
        :return:
        """
        buyer_tem = self.tem_buyer.copy()
        tem_seller = self.tem_seller.copy()
        satisfy_yixiang="0"
        number = buyer_tem.loc[buyer_index, '购买货物数量']
        tem_seller = tem_seller.sort_values(by=['货物数量（张）'], ascending=True)
        for i in tem_seller.index:
            seller_id=tem_seller.loc[i]['卖方客户']
            good_id=tem_seller.loc[i]['货物编号']
            ware_id=tem_seller.loc[i]['仓库']
            good_num=tem_seller.loc[i]['货物数量（张）']
            if good_num==0:
                break
            index = i
            if good_num >= number:
                tem_seller.loc[i,'货物数量（张）'] = good_num - number
                self.tem_seller.loc[i,'货物数量（张）'] = good_num - number  ##真实的记录下来
                self.seller.loc[i,'货物数量（张）']=good_num - number
                self.result.append([buyer_id, seller_id, var, good_id, ware_id, number, satisfy_yixiang])
                number = 0
                break
            else:
                self.result.append([buyer_id, seller_id, var, good_id, ware_id, good_num, satisfy_yixiang])
                number = number - good_num
                tem_seller.loc[i,'货物数量（张）'] = 0  #tem_seller.loc[i]['货物数量（张）'] -good_num
                self.tem_seller.loc[i,'货物数量（张）'] =0  # self.tem_seller.loc[i]['货物数量（张）']-good_num
                self.seller.loc[i, '货物数量（张）']=0
                if number==0:
                    break
        self.tem_buyer.loc[buyer_index, '购买货物数量'] = number
        self.buyer.loc[buyer_index, '购买货物数量'] = number

    def search_by_noyixiang(self):
        """
        与search_sameyixiang相似，只是不需要在乎意向
        :return:
        """
        for var in ["SR","CF"]:
            self.tem_seller=self.seller[self.seller['品种']==var]
            self.tem_buyer=self.buyer[self.buyer['品种']==var]
            self.tem_buyer=self.tem_buyer.sort_values(by=['购买货物数量'], ascending=True)
            buyer_tem_len = len(self.tem_buyer)
            print("该情况下买方用户的数量", buyer_tem_len)
            for i, buyer_index in enumerate(self.tem_buyer.index):
                buy_id=self.tem_buyer.loc[buyer_index,'买方客户']
                if i==buyer_tem_len-1:
                    print("第几个买家：", i + 1, "多少买家:", buyer_tem_len, "买家id:", buy_id, "时间:", datetime.datetime.now(),sum(self.buyer['购买货物数量'])==sum(self.seller['货物数量（张）']))
                self.search_by_noyixiang_onebuy(buy_id,var,buyer_index)
                self.tem_seller = self.tem_seller[self.tem_seller['货物数量（张）'] > 0]
                if i==buyer_tem_len-1:
                    print("该意向下还剩下多少卖家：", len(self.tem_seller))
            self.seller=self.seller[self.seller['货物数量（张）']>0]
            self.buyer=self.buyer[self.buyer['购买货物数量']>0]
            print("目前剩下多少买家：",len(self.buyer))
            print("目前剩下多少卖家：",len(self.seller))

    def sort_by_xiyang(self):
        """
        从第一意向到第五意向搜索。
        :return:
        """
        if self.tem_yixiang_index<5:
            self.tem_yixiang = list(self.yixiang2value.keys())[self.tem_yixiang_index]
            tem_buyer=self.buyer[~pd.isna(self.buyer[self.tem_yixiang])]
            tem_yixiang_value=self.yixiang2value[self.tem_yixiang]
            emotions = list(set(tem_buyer[tem_yixiang_value]))
            emotions_and_good = []
            for i in emotions:
                tem1 = tem_buyer[(tem_buyer[tem_yixiang_value] == i) & (tem_buyer['品种'] == 'SR')]["购买货物数量"].sum()
                tem2 = tem_buyer[(tem_buyer[tem_yixiang_value] == i) & (tem_buyer['品种'] == 'CF')]["购买货物数量"].sum()
                emotions_and_good.append((i, "SR", tem1, tem1 * self.SR_value[self.tem_yixiang_index]))
                emotions_and_good.append((i, "CF", tem2, tem2 * self.CF_value[self.tem_yixiang_index]))

            emotions_and_good=[i for i in emotions_and_good if i[2]>0]
            emotions_and_good = sorted(emotions_and_good, key=lambda x: x[3])#[::-1]
            self.search_sameyixiang(emotions_and_good)


    def main(self):
        for i in range(0,5):
            self.tem_yixiang_index=i
            self.sort_by_xiyang()
        self.search_by_noyixiang()

sol=solution(seller,buyer)
sol.main()
# res=pd.read_csv('result_format_example.csv',encoding='gbk')
# col=res.columns.to_list()
# resu=pd.DataFrame(sol.result,columns=col)
# resu.to_csv(r"result.txt",sep=",",columns=col,index=False)