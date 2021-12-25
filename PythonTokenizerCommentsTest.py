# This is a sample Python script.
# conding=utf8
import os
import  pandas as pd
import  tokenize
# 测试python注释的提取

fileObj = open('PythonComments.py', 'rb')

MULTI_COMMENT_INDEX=-1
MULTI_COMMENTS=""
for toktype, tok, start, end, line in tokenize.tokenize(fileObj.readline):
    # we can also use token.tok_name[toktype] instead of 'COMMENT'
    # from the token module
    # print("解析一行代码开始")
    # print(toktype,",", tok, ",",start, end, line)

    #多行的特征是后面一行的start与前面一行的start相差为1
    if toktype == tokenize.COMMENT:
        print('COMMENT' + " " + tok,start)
        if MULTI_COMMENT_INDEX==-1:
            MULTI_COMMENT_INDEX=start[0]
            MULTI_COMMENTS=tok.replace("#","").lower()
        else:
            if start[0]-MULTI_COMMENT_INDEX==1:
                MULTI_COMMENTS=MULTI_COMMENTS+tok.replace("#","").lower()
                MULTI_COMMENT_INDEX=MULTI_COMMENT_INDEX+1
            else:
                print("计算得到的注释：",MULTI_COMMENTS)
                # 计算得到多行注释以后设定下一行参数，开始处理下一行
                MULTI_COMMENT_INDEX=start[0]
                MULTI_COMMENTS=tok.replace("#","").lower()
print("最后一条多行注释",MULTI_COMMENTS)

    # print("解析一行代码结束")


exit()