import pandas as pd
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
        self.yixiang2value={"第一意向":'值','第二意向':'值.1','第三意向':'值.2','第四意向':'值.3','第五意向':'值.4'}
        self.SR_value=[40,30,20,10,0]
        self.CF_value=[33,27,20,13,7]
        self.tem_yixiang_index=0
        self.tem_yixiang=list(self.yixiang2value.keys())[self.tem_yixiang_index]

    def search_for_one_buyer(self,var,yixiangs,buyer_id,buyer_index):
        tem_seller=self.tem_seller.copy()
        number =self.tem_buyer.loc[buyer_index,'购买货物数量']#.values[0]

        satisfy_yixiang=[]
        for i, (yixiang, yixiang_value) in enumerate(yixiangs):
            if pd.isna(yixiang):
                continue
            if yixiang == '仓库' or yixiang == '年度':
                yixiang_value = int(yixiang_value)

            temp=tem_seller[tem_seller[yixiang] == yixiang_value] ##   其实第三意向后
            if len(temp)<=0:
                continue
            b = temp.groupby(['仓库'])['货物数量（张）'].sum().sort_values(ascending = False)
            if  b.values[0]>=number or sum(b)==sum(tem_seller['货物数量（张）']): ##那么肯定可以进入下一个意向
                tem_seller = tem_seller[tem_seller[yixiang] == yixiang_value]
            else:
                ##这种情况代表需要使用到多个仓库
                a = tem_seller.groupby(['仓库'])['货物数量（张）'].sum().sort_values(ascending=False)
                a_num=0
                for j in range(len(a)):
                    if sum(a[:j+1])>=number:
                        a_num=j+1
                        break
                b_num=100000
                for j in range(len(b)):
                    if sum(b[:j+1])>=number:
                        b_num=j+1
                        break
                if b_num-a_num==1 and self.tem_yixiang_index==0 and i==1:  ##a的值肯定小于等于b的值， sum(a)>=number
                    tem_seller = tem_seller[tem_seller[yixiang] == yixiang_value]  ##为了第二第三意向可以妥协
                elif b_num - a_num ==0:
                    tem_seller = tem_seller[tem_seller[yixiang] == yixiang_value]  ##如果需要的仓库数是一样的，并且可以满足意向，那么肯定选择它啊
                else:
                    ##如果进来的tem_seller不满足需求，那么上面的a肯定为0，b肯定为100000，那么肯定就会到这一步，tem_seller不做任何变化
                    tem_seller = tem_seller

        ab=tem_seller.groupby(['仓库'])['货物数量（张）'].sum()
        tem_seller['仓库总数量']=tem_seller['仓库'].map(ab)
        ##接下来的根据意向排序
        var = self.tem_buyer.loc[buyer_index,'品种']
        if var=="SR":
            weight = self.SR_value
        else:
            weight = self.CF_value
        tem_seller.loc[tem_seller.index, '权重1']=0
        for j, (yixiang, yixiang_value) in enumerate(yixiangs):
            if pd.isna(yixiang):
                continue
            if yixiang == '仓库' or yixiang == '年度':
                yixiang_value = int(yixiang_value)
            tem_seller.loc[tem_seller.index, '权重1']=tem_seller.loc[tem_seller.index, '权重1'] +(tem_seller.loc[tem_seller.index, yixiang]== yixiang_value).astype(int)*weight[self.tem_yixiang_index+j]

        maybe_ware=[]
        for j in ab.index:
            tem_sum=ab.loc[j]
            if tem_sum>=number:
                maybe_ware.append(j)
        if var=='CF'and len(maybe_ware)>1:
            max_hope_score=0
            max_ware=0
            for j in maybe_ware:
                tem_number=number
                tem_hope_score=0
                tempp=tem_seller[tem_seller['仓库']==j]
                tempp=tempp.sort_values(by=['权重1','货物数量（张）'], ascending=False)
                for k in tempp.index:
                    ware_num_i=tempp.loc[k,'货物数量（张）']
                    ware_wei_i=tempp.loc[k,'权重1']
                    if tem_number>=ware_num_i:
                        tem_hope_score+=ware_num_i*ware_wei_i
                        tem_number=tem_number-ware_num_i
                    elif tem_number<ware_num_i:
                        tem_hope_score += tem_number * tem_number
                        break
                if tem_hope_score>=max_hope_score:
                    if tem_hope_score==max_hope_score:
                        sum11= sum(tem_seller[tem_seller['仓库']==max_ware]['货物数量（张）'])
                        sum12= sum(tempp['货物数量（张）'])
                        if sum12>sum11:
                            max_hope_score=tem_hope_score
                            max_ware=j
                    else:
                        max_hope_score = tem_hope_score
                        max_ware = j
            tem_seller=tem_seller[tem_seller['仓库']==max_ware]
            tem_seller=tem_seller.sort_values(by=['仓库总数量','权重1','货物数量（张）'], ascending=False)
        else:
            tem_seller = tem_seller.sort_values(by=['仓库总数量','权重1','货物数量（张）'], ascending=False)

        for i in tem_seller.index:
            seller_id=tem_seller.loc[i]['卖方客户']
            good_id=tem_seller.loc[i]['货物编号']
            ware_id=tem_seller.loc[i]['仓库']
            good_num=tem_seller.loc[i]['货物数量（张）']
            pinpai_id=tem_seller.loc[i]['品牌']
            year_id=tem_seller.loc[i]['年度']
            grade_id=tem_seller.loc[i]['等级']
            vari_id=tem_seller.loc[i]['类别']
            dis_id=tem_seller.loc[i]['产地']
            if good_num<=0:
                break
            set_yixiang=[pinpai_id,year_id,grade_id,vari_id,dis_id,ware_id]
            satisfy_yixiang_1=satisfy_yixiang.copy()

            for j, (yixiang, yixiang_value) in enumerate(yixiangs):
                if pd.isna(yixiang):
                    continue
                if yixiang == '仓库' or yixiang == '年度':
                    yixiang_value = int(yixiang_value)
                if yixiang_value in set_yixiang:
                    satisfy_yixiang_1.append(str(j + self.tem_yixiang_index + 1))
            if len(satisfy_yixiang_1)==0:
                satisfy_yixiang_1=['0']
            if good_num >= number:
                tem_seller.loc[i,'货物数量（张）'] = good_num - number
                self.tem_seller.loc[i,'货物数量（张）'] = good_num - number  ##真实的记录下来
                self.seller.loc[i,'货物数量（张）']=good_num - number
                self.result.append([buyer_id, seller_id, var, good_id, ware_id, number, '-'.join(satisfy_yixiang_1)])
                number = 0
                break
            else:
                self.result.append([buyer_id, seller_id, var, good_id, ware_id, good_num, '-'.join(satisfy_yixiang_1)])
                number = number - good_num
                tem_seller.loc[i,'货物数量（张）'] = 0  #tem_seller.loc[i]['货物数量（张）'] -good_num
                self.tem_seller.loc[i,'货物数量（张）'] =0  # self.tem_seller.loc[i]['货物数量（张）']-good_num
                self.seller.loc[i, '货物数量（张）']=0
                if number==0:
                    break
        self.tem_buyer.loc[buyer_index,'购买货物数量']=number
        self.buyer.loc[buyer_index,'购买货物数量']=number

    def getorder(self,buyer_tm,var,col1):
        if var == "SR":
            weight = self.SR_value
            for i in range(self.tem_yixiang_index, 4):
                buyer_tm.loc[buyer_tm.index, '权值系数'] = buyer_tm.loc[buyer_tm.index, '权值系数'] + pd.notna(buyer_tm.loc[buyer_tm.index, col1[i]]).astype(int) * weight[i]
        else:
            weight =self.CF_value
            for i in range(self.tem_yixiang_index, 5):
                buyer_tm.loc[buyer_tm.index, '权值系数'] = buyer_tm.loc[buyer_tm.index, '权值系数'] + pd.notna(
                    buyer_tm.loc[buyer_tm.index, col1[i]]).astype(int) * weight[i]
        buyer_tm.loc[buyer_tm.index, '权重'] = buyer_tm.loc[buyer_tm.index, '权值系数'] * buyer_tm.loc[buyer_tm.index, '购买货物数量']
        return buyer_tm

    def search_sameyixiang(self, emotions_and_good):
        for dis, var, sum1, rate in emotions_and_good:
            print(dis, var, sum1, rate)
            if sum1 <= 0:
                continue
            thefirst = self.buyer[self.buyer[self.yixiang2value[self.tem_yixiang]] == dis][self.tem_yixiang].iloc[0]

            self.tem_buyer = self.buyer[
                (self.buyer[self.yixiang2value[self.tem_yixiang]] == dis) & (self.buyer['品种'] == var)]
            if thefirst == '年度' or thefirst == '仓库':
                dis = int(dis)

            if self.tem_yixiang_index == 0:
                self.tem_seller = self.seller[
                    (self.seller[thefirst] == dis) & (self.seller['品种'] == var)]  ##如果能够满足第一第二意向的话，还是满足，否则直接从全量中搜索
            else:
                self.tem_seller = self.seller[(self.seller['品种'] == var)]

            if sum(self.tem_seller['货物数量（张）']) == 0:  # 如果满足这个意向的货物没有了，那么就不需要了
                continue
            sum_dis = min( sum(self.tem_seller['货物数量（张）']), sum(self.tem_buyer['购买货物数量']))

            print("当前是第几意向：", self.tem_yixiang_index, "  第几轮：", "  seller数量:", len(self.tem_seller),
                  '   该意向下Buyer数量:', len(self.tem_buyer), '  买方的总数量:', sum(self.tem_buyer['购买货物数量']), '   卖方总数量:',
                  sum(self.tem_seller['货物数量（张）']), "  应该取多少进行分配:", sum_dis)

            self.tem_buyer.loc[self.tem_buyer.index, '权值系数'] = 0
            self.tem_buyer = self.getorder(self.tem_buyer, var, list(self.yixiang2value.keys()).copy())

            if self.tem_yixiang_index == 0:
                self.tem_buyer = self.tem_buyer.sort_values(by=['平均持仓时间', '权重'], ascending=False)
            else:
                self.tem_buyer = self.tem_buyer.sort_values(by=['权重'], ascending=False)
            sum_seller = sum_dis
            flag = False
            for ii, ij in enumerate(self.tem_buyer.index):
                temp1 = self.tem_buyer.loc[ij, '购买货物数量']
                if sum_seller >= temp1:  ##这次就可以超过你了
                    sum_seller = sum_seller - temp1
                else:
                    ##把前面哪些人供应好了就可以了，后面的可以不管
                    tem_buyer1 = self.tem_buyer[:ii]
                    tem_buyer2 = self.tem_buyer[ii:ii + 1]
                    flag = True
                    break
            if flag:
                tem_buyer1 = tem_buyer1.sort_values(by=['权重'], ascending=False)
                self.tem_buyer = pd.concat([tem_buyer1, tem_buyer2])
            else:
                self.tem_buyer = self.tem_buyer.sort_values(by=['权重'], ascending=False)  ##这里之后可以改下
                print('tt')
            buyer_tem_len = len(self.tem_buyer)

            for i, buyer_index in enumerate(self.tem_buyer.index):
                buyer_id = self.tem_buyer.loc[buyer_index, '买方客户']
                if i == buyer_tem_len - 1:
                    print("第几个买家：", i + 1, "多少买家:", buyer_tem_len, "买家id:", buyer_id, "时间:", datetime.datetime.now(),
                          sum(self.buyer['购买货物数量']) == sum(self.seller['货物数量（张）']))  #
                if sum(self.tem_seller['货物数量（张）']) == 0:  ##如果满足意向的货物没有了，那么后面的都不需要再满足了。
                    break
                yixiangs = []

                for j in range(self.tem_yixiang_index, len(self.yixiang2value)):
                    yixiang = list(self.yixiang2value.keys())[j]
                    yixiang_value = self.yixiang2value[yixiang]
                    yixiangs.append(yixiang)
                    yixiangs.append(yixiang_value)
                tt = self.tem_buyer[self.tem_buyer.index == buyer_index][yixiangs]
                tt = tt.values[:1].tolist()[0]
                yixiangs = [(tt[k], tt[k + 1]) for k in range(0, len(tt), 2)]

                self.search_for_one_buyer(var, yixiangs, buyer_id, buyer_index)
                self.tem_seller = self.tem_seller[self.tem_seller['货物数量（张）'] > 0]
                if i == buyer_tem_len - 1:
                    print("该意向下还剩下多少卖家：", len(self.tem_seller))
            self.seller = self.seller[self.seller['货物数量（张）'] > 0]
            self.buyer = self.buyer[self.buyer['购买货物数量'] > 0]
            print("目前剩下多少买家：", len(self.buyer))
            print("目前剩下多少卖家：", len(self.seller))

    def search_by_noyixiang_onebuy(self,buyer_id,var,buyer_index):
        buyer_tem = self.tem_buyer.copy()
        tem_seller = self.tem_seller.copy()
        satisfy_yixiang="0"
        number = buyer_tem.loc[buyer_index, '购买货物数量']
        b=tem_seller.groupby(['仓库'])['货物数量（张）'].sum()
        tem_seller['仓库总数量']=tem_seller['仓库'].map(b)
        tem_seller = tem_seller.sort_values(by=['仓库总数量','货物数量（张）'], ascending=False)
        for i in tem_seller.index:
            seller_id=tem_seller.loc[i]['卖方客户']
            good_id=tem_seller.loc[i]['货物编号']
            ware_id=tem_seller.loc[i]['仓库']
            good_num=tem_seller.loc[i]['货物数量（张）']
            if good_num==0:
                break
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
        for var in ["SR","CF"]:
            self.tem_seller=self.seller[self.seller['品种']==var]
            self.tem_buyer=self.buyer[self.buyer['品种']==var]
            self.tem_buyer=self.tem_buyer.sort_values(by=['购买货物数量'], ascending=False)
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
        while self.tem_yixiang_index<5:
            self.tem_yixiang = list(self.yixiang2value.keys())[self.tem_yixiang_index]
            tem_buyer=self.buyer[~pd.isna(self.buyer[self.tem_yixiang])]
            tem_yixiang_value=self.yixiang2value[self.tem_yixiang]
            emotions = list(set(tem_buyer[tem_yixiang_value]))
            emotions_and_good = []
            j=0
            for i in emotions:
                tem1 = tem_buyer[(tem_buyer[tem_yixiang_value] == i) & (tem_buyer['品种'] == 'SR')]["购买货物数量"].sum()
                tem2 = tem_buyer[(tem_buyer[tem_yixiang_value] == i) & (tem_buyer['品种'] == 'CF')]["购买货物数量"].sum()
                thefirst = self.buyer[self.buyer[self.yixiang2value[self.tem_yixiang]] == i][self.tem_yixiang].iloc[0]
                if thefirst == '年度' or thefirst == '仓库':
                    j = int(i)
                    temp1= self.tem_seller=self.seller[(self.seller[thefirst]==j) & (self.seller['品种']=='SR')]['货物数量（张）'].sum()
                    temp2 = self.tem_seller=self.seller[(self.seller[thefirst]==j) & (self.seller['品种'] == 'CF')]['货物数量（张）'].sum()
                else:
                    temp1 = self.tem_seller = self.seller[(self.seller[thefirst] == i) & (self.seller['品种'] == 'SR')][
                        '货物数量（张）'].sum()
                    temp2 = self.tem_seller = self.seller[(self.seller[thefirst] == i) & (self.seller['品种'] == 'CF')][
                        '货物数量（张）'].sum()

                emotions_and_good.append((i, "SR", tem1, round(tem1/(temp1+0.1),1))) #本来是1，改成2
                emotions_and_good.append((i, "CF", tem2,  round(tem2/(temp2+0.1),1)))
            emotions_and_good = [i for i in emotions_and_good if i[2] > 0]
            emotions_and_good = sorted(emotions_and_good, key=lambda x: [x[3],x[2]])[::-1]##越大说明越紧急
            self.search_sameyixiang(emotions_and_good)
            self.tem_yixiang_index+=1
    def main(self):
        self.sort_by_xiyang()
        self.search_by_noyixiang()

sol=solution(seller,buyer)
sol.main()
res=pd.read_csv('result_format_example.csv',encoding='gbk')
col=res.columns.to_list()
resu=pd.DataFrame(sol.result,columns=col)
resu.to_csv(r"result_l.txt",sep=",",columns=col,index=False,encoding='gbk')