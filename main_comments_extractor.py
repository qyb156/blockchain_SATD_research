# This is a sample Python script.
# conding=utf8
import os
import  pandas as pd
import  tokenize
import  re

# strHaicoder = "-1024"
# print("isnumeric =", strHaicoder.isnumeric())
#
# a="1"
#
# print ("a", re.match(r"d+$", a) and True or False)
# print(re.match(r'[+-]?\d+$', '-1234'))
#
# exit()
import xml.etree.ElementTree as ET

'''
当过滤的项目为比特币项目的时候，解析xml文件中的代码评论，合并到非C++语言的代码评论中。
'''
def parseXML(xmlFile,pdres):
    """
    Parse the xml
    """
    # pdres=pd.DataFrame([])
    print(pdres.shape)
    tree = ET.parse(xmlFile)
    walkAll = tree.getroot()
    print("root",walkAll.tag,walkAll.attrib)
    for child in walkAll:
        # print("child",child.tag, ":",child.attrib['filename'])
        # 在这里遍历子节点，也就是遍历每个文件
        for emt in child.iter():
            fullname=child.attrib['filename']
            # print(emt)
            if "comment" in emt.tag:
                tmpcomment = emt.text
                # print(tmpcomment)
                # 剔除常见的无用标示符
                tmpcomment=tmpcomment.replace("/"," ")
                tmpcomment = tmpcomment.replace("*", " ")
                tmpcomment = tmpcomment.replace("#", " ")
                tmpcomment = tmpcomment.replace(";", " ")
                tmpcomment = tmpcomment.replace("!", " ")
                tmpcomment = tmpcomment.replace("-", " ")
                if tmpcomment.strip() != "":
                    pdres = pdres.append(
                        [[fullname, GetSATDLabel(tmpcomment), tmpcomment.lower().strip(), GetFilterLabel(tmpcomment)]],
                        ignore_index=True)

    print(pdres.shape)
    return pdres
            # exit()
    # pdres.to_excel("bitcoin_c_.xlsx")

'''
# 考虑过滤掉那些说明文字,
'''
def GetFilterLabel(tmpcomment):
    if "copyright" in tmpcomment.lower() \
            or "code generated" in tmpcomment.lower()\
            or "mit software license" in tmpcomment.lower() \
            or  "spdx-license-identifier" in tmpcomment.lower()\
            or  "/usr/bin/env" in tmpcomment.lower()\
            or tmpcomment.lower().isnumeric()\
            or "Distributed under the MIT software license" in tmpcomment.lower() \
            or "file COPYING" in tmpcomment.lower():

        return "ready_to_filter"
    else:
        return "unlabelled"

# 根据标注的情况来看,有些关键词可以用于匹配SATD,比如todo,current,currently,future,error,errors,test,however,but,
# now,bug,bugs,not correctly,segfault,would,should,incorrect,duplicate,not set,not exist,never,issue,issues
#fail,temporary,cause,invalid,illegal,false positive,fails,not reachable,removed,not okay,untrue,won't,
# exception,unsupported,workaround,non optimized,fatal,be optimized,not reachable
'''
# 根据用到的关键词,进行初步模糊匹配一下,
'''
def GetSATDLabel(tmpcomment):
    # # 作为design类型的关键词
    # keywordlist=["todo","current","currently","future","error",
    #              "errors","however","but","now","bug","bugs",
    #              "not correctly","segfault","would","should",
    #              "incorrect","duplicate","not set","not exist","never",
    #              "issue","issues","fail","temporary","cause","invalid",
    #              "illegal","false positive","fails","not reachable",
    #              "removed","not okay","untrue","won't","exception",
    #              "unsupported","workaround","non optimized","fatal",
    #              "be optimized","not reachable"]

    keywordlist = ["todo", "issue", "issues", "fail", "temporary", "xxx", "fixme",
                   "hack"]

    for word in keywordlist:
        if word in tmpcomment.lower() :
            return "design"
    # 作为test类型的关键词
    if "test" in tmpcomment.lower() :
            return "test"

    # # 作为document类型的关键词
    # if "document"  in tmpcomment.lower() or\
    #         "documents"  in tmpcomment.lower():
    #     return "document"

    return "WITHOUT_SATD"

def Tokenizer(projectname,path):
    # 创建空的pd
    # pdres=pd.DataFrame([],columns=["id","path","comments","is_filtered","type"])
    pdres = pd.DataFrame([])
    # projectname="go-ethereum-master"
    # base = ".\\"+projectname
    # print(base)
    # exit()

    # 统计源代码文件的数目
    number_of_soucecode_file=0

    loc=0
    for root, ds, fs in os.walk(path):
        for f in fs:
            tmpcomment=""
            fullname = os.path.join(root, f)
            if f.endswith('.go')  or  f.endswith('.sol') or  f.endswith('.rs') :
                number_of_soucecode_file=number_of_soucecode_file+1
                file = open(fullname, encoding='utf-8')
                print(fullname)
                lines = file.readlines()

                # 定义一个/*  */多行注释的开始标记
                MULTI=False
                for line in lines:
                    line = line.strip()
                    # 如果line值为空,则表示是空行,跳出循环继续执行
                    if len(line)==0:
                        continue

                    if MULTI==False:
                        if line.startswith("//"):
                            tmpcomment=tmpcomment+ line.replace("/"," ")
                        elif line.startswith("/*"):
                            tmpcomment  =tmpcomment+ line.replace("/*"," ")
                            MULTI=True
                        else:
                            # 如果既不是"//"开头,也不是/*开头,那应该就是代码了,那就结束多行注释的循环或者是单行注释,直接写结果
                            # 可能潜存一种情况,注释在最后面,接下来没有代码,那也就时没有意义的注释行,不写结果影响也不大。
                            if tmpcomment.strip()!="":
                                pdres = pdres.append([[fullname,GetSATDLabel(tmpcomment), tmpcomment.lower().strip(), GetFilterLabel(tmpcomment)]], ignore_index=True)
                                tmpcomment=""
                    else:
                       #  表示/*  */多行注释结束了。
                       if line.startswith("*/"):
                        # print(line)
                            tmpcomment = line.replace("*/", " ")
                            MULTI=False
                            if tmpcomment.strip() != "":
                                pdres = pdres.append([[fullname, GetSATDLabel(tmpcomment), tmpcomment.lower().strip(), GetFilterLabel(tmpcomment)]], ignore_index=True)
                                tmpcomment = ""
                            # print(pdres)
                       else:
                           tmpcomment = tmpcomment + line.replace("*", " ")
                file.close()
            elif  f.endswith('.py') :
                number_of_soucecode_file = number_of_soucecode_file + 1
                fileObj = open(fullname, 'rb')
                # fileObj = open('PythonComments.py', 'rb')

                MULTI_COMMENT_INDEX = -1
                MULTI_COMMENTS = ""
                for toktype, tok, start, end, line in tokenize.tokenize(fileObj.readline):
                    # we can also use token.tok_name[toktype] instead of 'COMMENT'
                    # from the token module
                    # print("解析一行代码开始")
                    # print(toktype,",", tok, ",",start, end, line)

                    # 多行的特征是后面一行的start与前面一行的start相差为1
                    if toktype == tokenize.COMMENT:
                        # print('COMMENT' + " " + tok, start)
                        if MULTI_COMMENT_INDEX == -1:
                            MULTI_COMMENT_INDEX = start[0]
                            MULTI_COMMENTS = tok.replace("#", " ").lower()
                        else:
                            if start[0] - MULTI_COMMENT_INDEX == 1:
                                MULTI_COMMENTS = MULTI_COMMENTS + tok.replace("#", " ").lower()
                                MULTI_COMMENT_INDEX = MULTI_COMMENT_INDEX + 1
                            else:
                                # print("计算得到的注释：", MULTI_COMMENTS)
                                if len(MULTI_COMMENTS.lower().strip())>0:
                                    pdres = pdres.append(
                                        [[fullname, GetSATDLabel(tmpcomment), MULTI_COMMENTS.lower().strip(), GetFilterLabel(MULTI_COMMENTS.lower().strip())]],
                                        ignore_index=True)
                                # 计算得到多行注释以后设定下一行参数,开始处理下一行
                                MULTI_COMMENT_INDEX = start[0]
                                MULTI_COMMENTS = tok.replace("#", " ").lower()
                # print("最后一条多行注释", MULTI_COMMENTS)
                if len(MULTI_COMMENTS.lower().strip()) > 0:
                    pdres = pdres.append(
                        [[fullname,GetSATDLabel(tmpcomment), MULTI_COMMENTS.lower().strip(), GetFilterLabel(MULTI_COMMENTS.lower().strip())]],
                        ignore_index=True)
                fileObj.close()
            # Rust的普通注释与C + + 的风格一样,分为：
            # 单行注释 - - 以 // 开头, // 后的内容都会被注释掉。
            # 块注释 - - 可以注释多行,并且可以嵌套,使用 / * ... * / 将注释内容与代码分隔。
            #
            # 示例：
            # fn
            # main()
            # {
            # // 这是行注释
            #
            # / * 这是块注释,
            # 可以注释多行。 * /
            #
            # / *
            # * 这也是块注释
            #   * 该行前面的星号不是必须的
            #   * 但这样比较好看
            #   * /
            #
            #   / * 块注释可以嵌套 / * 嵌套有什么用？ * / 我很疑惑 * /
            #
            #                               // 块注释可以注释掉一行中间的部分代码,行注释则没有这个能力
            # let
            # x = 5 + / *90 + * / 5;
            # println!("Is `x` 10 or 100? x = {}", x);
            # }
            # 分拆字符串
            # strComments=strComments.replace("____","$")
            # ____________________________________________ NewFileBasedKeyStore instantiated a file-based key store at a given position.
            # strCommentsList=strComments.split("_")
            # # print(strCommentsList)
            # # exit()
            # for comment in strCommentsList:
            #     if len(comment)==0:
            #         # print(comment)
            #         continue
            #     pdres = pdres.append([comment], ignore_index=True)

    # pdres.to_csv(str(projectname)+".csv")

    if "bitcoin-22.0" in projectname:
        pdres=parseXML("bitcoin.xml",pdres)
        pdres.to_excel("result//"+str(projectname) + "_countofFiles_" + str(number_of_soucecode_file+1726) + ".xlsx")
    else:
        pdres.to_excel("result//"+str(projectname)+"_countofFiles_"+str(number_of_soucecode_file)+ ".xlsx")


def calTags():
    # 统计任务标志出现的次数
    proecessed_projects = ["bitcoin", "ethereum", "diem", "solidity", "fabric", "chia"]
    # proecessed_projects = ["fabric"]
    taskTags = ["todo", "fixme", "xxx", "hack"]

    pd_proecessed_projects = pd.DataFrame([])
    path = ".\\preprocessed_datasets"
    pd_proecessed_projects = pd_proecessed_projects.append(
        [
            [
                "Project", "SATD Types", "#Count", "todo", "fixme", "xxx", "hack", "#All Tags", "#Percent"
            ]
        ],
        ignore_index=True)

    for tmpproject in proecessed_projects:
        for root, ds, fs in os.walk(path):
            for f in fs:
                tmpcomment = ""
                fullname = os.path.join(root, f)

                if tmpproject in fullname:
                    todo_WITHOUT_SATD = 0
                    fixme_WITHOUT_SATD = 0
                    xxx_WITHOUT_SATD = 0
                    hack_WITHOUT_SATD = 0
                    WITHOUT_SATD = 0

                    todo_SATD = 0
                    fixme_SATD = 0
                    xxx_SATD = 0
                    hack_SATD = 0
                    SATD = 0

                    todo_UNCHECKED = 0
                    fixme_UNCHECKED = 0
                    xxx_UNCHECKED = 0
                    hack_UNCHECKED = 0
                    UNCHECKED = 0

                    print(fullname)
                    # 读取文件
                    tmppd = pd.read_excel(fullname)
                    # print(tmppd)
                    for i in range(len(tmppd)):
                        # print(tmppd.iloc[i,0],tmppd.iloc[i,1],tmppd.iloc[i,2],tmppd.iloc[i,3],tmppd.iloc[i,4])
                        comments = str(tmppd.iloc[i, 3]).lower()
                        # print(tmppd)
                        # print(comments)
                        # exit()
                        if tmppd.iloc[i, 4] == "unlabelled":
                            if tmppd.iloc[i, 2] == "WITHOUT_SATD":
                                WITHOUT_SATD = WITHOUT_SATD + 1
                                if "todo" in comments:
                                    todo_WITHOUT_SATD = todo_WITHOUT_SATD + 1
                                    continue
                                elif "fixme" in comments:
                                    fixme_WITHOUT_SATD = fixme_WITHOUT_SATD + 1
                                    continue
                                elif "xxx" in comments:
                                    xxx_WITHOUT_SATD = xxx_WITHOUT_SATD + 1
                                    continue
                                elif "hack" in comments:
                                    hack_WITHOUT_SATD = hack_WITHOUT_SATD + 1
                                    continue
                            elif tmppd.iloc[i, 2] == "UNCHECKED":
                                UNCHECKED = UNCHECKED + 1
                                if "todo" in comments:
                                    todo_UNCHECKED = todo_UNCHECKED + 1
                                    continue
                                elif "fixme" in comments:
                                    fixme_UNCHECKED = fixme_UNCHECKED + 1
                                    continue
                                elif "xxx" in comments:
                                    xxx_UNCHECKED = xxx_UNCHECKED + 1
                                    continue
                                elif "hack" in comments:
                                    hack_UNCHECKED = hack_UNCHECKED + 1
                                    continue
                            else:
                                SATD = SATD + 1
                                if "todo" in comments:
                                    todo_SATD = todo_SATD + 1
                                    continue
                                elif "fixme" in comments:
                                    fixme_SATD = fixme_SATD + 1
                                    continue
                                elif "xxx" in comments:
                                    xxx_SATD = xxx_SATD + 1
                                    continue
                                elif "hack" in comments:
                                    hack_SATD = hack_SATD + 1
                                    continue

                    pd_proecessed_projects = pd_proecessed_projects.append(
                        [
                            [
                                tmpproject, "SATD", str(SATD), str(todo_SATD), str(fixme_SATD), str(xxx_SATD),
                                str(hack_SATD), str(todo_SATD + fixme_SATD + xxx_SATD + hack_SATD),
                                str(round((todo_SATD + fixme_SATD + xxx_SATD + hack_SATD) / SATD, 4) * 100) + str("%")
                            ]
                        ],
                        ignore_index=True)

                    pd_proecessed_projects = pd_proecessed_projects.append(
                        [
                            [
                                tmpproject, "UNCHECKED debt", str(UNCHECKED), str(todo_UNCHECKED), str(fixme_UNCHECKED),
                                str(xxx_UNCHECKED), str(hack_UNCHECKED),
                                str(todo_UNCHECKED + fixme_UNCHECKED + xxx_UNCHECKED + hack_UNCHECKED)
                                , str(round(
                                (todo_UNCHECKED + fixme_UNCHECKED + xxx_UNCHECKED + hack_UNCHECKED) / UNCHECKED,
                                4) * 100) + str("%")
                            ]
                        ],
                        ignore_index=True)

                    pd_proecessed_projects = pd_proecessed_projects.append(
                        [
                            [
                                tmpproject, "WITHOUT_SATD", str(WITHOUT_SATD), str(todo_WITHOUT_SATD),
                                str(fixme_WITHOUT_SATD),
                                str(xxx_WITHOUT_SATD), str(hack_WITHOUT_SATD),
                                str(todo_WITHOUT_SATD + fixme_WITHOUT_SATD + xxx_WITHOUT_SATD + hack_WITHOUT_SATD)
                                , str(round((
                                                        todo_WITHOUT_SATD + fixme_WITHOUT_SATD + xxx_WITHOUT_SATD + hack_WITHOUT_SATD) / WITHOUT_SATD,
                                            4) * 100) + str("%")
                            ]
                        ],
                        ignore_index=True)

                    pd_proecessed_projects.to_excel(".\\result\\tags.xlsx", index=False)


def calPropotionOfSATD():
    # 统计任务标志出现的次数
    proecessed_projects = ["bitcoin", "ethereum", "diem", "solidity", "fabric", "chia"]
    proecessed_projects_files = {"bitcoin":1959, "ethereum":2256, "diem":1312, "solidity":5573, "fabric":3826, "chia":412}
    # proecessed_projects = ["fabric"]
    taskTags = ["todo", "fixme", "xxx", "hack"]

    pd_proecessed_projects = pd.DataFrame([])
    path = ".\\preprocessed_datasets"
    pd_proecessed_projects = pd_proecessed_projects.append(
        [
            [
               "Granularity",  "Project",  "#Total", "#SATD",  "%"
            ]
        ],
        ignore_index=True)

    for tmpproject in proecessed_projects:
        for root, ds, fs in os.walk(path):
            for f in fs:
                tmpcomment = ""
                fullname = os.path.join(root, f)

                if tmpproject in fullname:
                    # todo_WITHOUT_SATD = 0
                    # fixme_WITHOUT_SATD = 0
                    # xxx_WITHOUT_SATD = 0
                    # hack_WITHOUT_SATD = 0
                    # WITHOUT_SATD = 0

                    todo_SATD = 0
                    fixme_SATD = 0
                    xxx_SATD = 0
                    hack_SATD = 0
                    SATD = 0
                    #
                    # todo_UNCHECKED = 0
                    # fixme_UNCHECKED = 0
                    # xxx_UNCHECKED = 0
                    # hack_UNCHECKED = 0
                    # UNCHECKED = 0

                    lenOfProject=0

                    print(fullname)
                    # 读取文件
                    tmppd = pd.read_excel(fullname)

                    path_set=set()

                    # print(tmppd)
                    for i in range(len(tmppd)):
                        # print(tmppd.iloc[i,0],tmppd.iloc[i,1],tmppd.iloc[i,2],tmppd.iloc[i,3],tmppd.iloc[i,4])
                        comments = str(tmppd.iloc[i, 3]).lower()
                        # print(tmppd)
                        # print(comments)
                        # exit()
                        if tmppd.iloc[i, 4] == "unlabelled":
                            # 把文件路径放到set里面去，保持不重复

                            # print(tmppd.iloc[i,1])
                            # print(path_set)
                            # exit()

                            lenOfProject=lenOfProject+1
                            if tmppd.iloc[i, 2] == "WITHOUT_SATD":
                                # WITHOUT_SATD = WITHOUT_SATD + 1
                                # if "todo" in comments:
                                #     todo_WITHOUT_SATD = todo_WITHOUT_SATD + 1
                                #     continue
                                # elif "fixme" in comments:
                                #     fixme_WITHOUT_SATD = fixme_WITHOUT_SATD + 1
                                #     continue
                                # elif "xxx" in comments:
                                #     xxx_WITHOUT_SATD = xxx_WITHOUT_SATD + 1
                                #     continue
                                # elif "hack" in comments:
                                #     hack_WITHOUT_SATD = hack_WITHOUT_SATD + 1
                                    continue
                            elif tmppd.iloc[i, 2] == "UNCHECKED":
                                SATD=SATD+1
                                path_set.add(tmppd.iloc[i, 1])
                                # UNCHECKED = UNCHECKED + 1
                                # if "todo" in comments:
                                #     todo_UNCHECKED = todo_UNCHECKED + 1
                                #     continue
                                # elif "fixme" in comments:
                                #     fixme_UNCHECKED = fixme_UNCHECKED + 1
                                #     continue
                                # elif "xxx" in comments:
                                #     xxx_UNCHECKED = xxx_UNCHECKED + 1
                                #     continue
                                # elif "hack" in comments:
                                #     hack_UNCHECKED = hack_UNCHECKED + 1
                                continue
                            else:
                                SATD = SATD + 1
                                path_set.add(tmppd.iloc[i, 1])
                                # if "todo" in comments:
                                #     todo_SATD = todo_SATD + 1
                                #     continue
                                # elif "fixme" in comments:
                                #     fixme_SATD = fixme_SATD + 1
                                #     continue
                                # elif "xxx" in comments:
                                #     xxx_SATD = xxx_SATD + 1
                                #     continue
                                # elif "hack" in comments:
                                #     hack_SATD = hack_SATD + 1
                                #     continue

                    pd_proecessed_projects = pd_proecessed_projects.append(
                        [
                            [
                                "Comment", tmpproject, str(lenOfProject), str(SATD),str(round(SATD  / lenOfProject, 4) * 100) + str("%")
                            ]
                        ],
                        ignore_index=True)

                    pd_proecessed_projects = pd_proecessed_projects.append(
                        [
                            [
                                "File", tmpproject, str(proecessed_projects_files[tmpproject]), str(len(path_set)),
                                str(round(len(path_set) / proecessed_projects_files[tmpproject], 4) * 100) + str("%")
                            ]
                        ],
                        ignore_index=True)
                    # pd_proecessed_projects = pd_proecessed_projects.append(
                    #     [
                    #         [
                    #             tmpproject, "UNCHECKED debt", str(UNCHECKED), str(todo_UNCHECKED), str(fixme_UNCHECKED),
                    #             str(xxx_UNCHECKED), str(hack_UNCHECKED),
                    #             str(todo_UNCHECKED + fixme_UNCHECKED + xxx_UNCHECKED + hack_UNCHECKED)
                    #             , str(round(
                    #             (todo_UNCHECKED + fixme_UNCHECKED + xxx_UNCHECKED + hack_UNCHECKED) / UNCHECKED,
                    #             4) * 100) + str("%")
                    #         ]
                    #     ],
                    #     ignore_index=True)
                    #
                    # pd_proecessed_projects = pd_proecessed_projects.append(
                    #     [
                    #         [
                    #             tmpproject, "WITHOUT_SATD", str(WITHOUT_SATD), str(todo_WITHOUT_SATD),
                    #             str(fixme_WITHOUT_SATD),
                    #             str(xxx_WITHOUT_SATD), str(hack_WITHOUT_SATD),
                    #             str(todo_WITHOUT_SATD + fixme_WITHOUT_SATD + xxx_WITHOUT_SATD + hack_WITHOUT_SATD)
                    #             , str(round((
                    #                                     todo_WITHOUT_SATD + fixme_WITHOUT_SATD + xxx_WITHOUT_SATD + hack_WITHOUT_SATD) / WITHOUT_SATD,
                    #                         4) * 100) + str("%")
                    #         ]
                    #     ],
                    #     ignore_index=True)

                    pd_proecessed_projects.to_excel(".\\result\\SATD_propotion.xlsx", index=False)



def cal_TD_propotion():
    # 统计任务标志出现的次数
    proecessed_projects = ["bitcoin", "ethereum", "diem", "solidity", "fabric", "chia"]

    pd_proecessed_projects = pd.DataFrame([])
    path = ".\\preprocessed_datasets"
    pd_proecessed_projects = pd_proecessed_projects.append(
        [
            [
                "Project", "#TD", "Design Debt", "Defect Debt", "Documentation Debt", "Requirement Debt", "Test Debt", "Compatibility Debt", "Algorithm Debt", "Unchecked Debt"
            ]
        ],
        ignore_index=True)

    for tmpproject in proecessed_projects:
        for root, ds, fs in os.walk(path):
            for f in fs:
                tmpcomment = ""
                fullname = os.path.join(root, f)
                # WITHOUT_SATD, defect, design, documentation, requirement, test, compatibility, algorithm, UNCHECKED
                if tmpproject in fullname:
                    defect=design=documentation=requirement=test=compatibility=algorithm=UNCHECKED=0
                    TD = 0
                    print(fullname)
                    # 读取文件
                    tmppd = pd.read_excel(fullname)
                    # print(tmppd)
                    for i in range(len(tmppd)):
                        # print(tmppd.iloc[i,0],tmppd.iloc[i,1],tmppd.iloc[i,2],tmppd.iloc[i,3],tmppd.iloc[i,4])
                        comments = str(tmppd.iloc[i, 3]).lower()
                        if tmppd.iloc[i, 4] == "unlabelled":
                            if tmppd.iloc[i, 2] == "defect":
                                defect=defect+1
                                TD=TD+1
                                continue
                            elif tmppd.iloc[i, 2] == "design":
                                design=design+1
                                TD = TD + 1
                                continue
                            elif tmppd.iloc[i, 2] == "design":
                                design = design + 1
                                TD = TD + 1
                                continue
                            elif tmppd.iloc[i, 2] == "documentation":
                                documentation=documentation+1
                                TD = TD + 1
                                continue
                            elif tmppd.iloc[i, 2] == "requirement":
                                requirement=requirement+1
                                TD = TD + 1
                                continue
                            elif tmppd.iloc[i, 2] == "test":
                                test=test+1
                                TD = TD + 1
                                continue
                            elif tmppd.iloc[i, 2] == "compatibility":
                                compatibility=compatibility+1
                                TD = TD + 1
                                continue
                            elif tmppd.iloc[i, 2] == "algorithm":
                                algorithm = algorithm + 1
                                TD = TD + 1
                                continue
                            elif tmppd.iloc[i, 2] == "UNCHECKED":
                                UNCHECKED = UNCHECKED + 1
                                TD = TD + 1
                                continue

                    pd_proecessed_projects = pd_proecessed_projects.append(
                        [
                            [
                                tmpproject, str(TD), str(round(defect/TD, 4) * 100)+ str("%"),str(round(design/ TD, 4) * 100)+ str("%"),
                    str(round(documentation/ TD, 4) * 100)+ str("%"),
                                str(round(requirement/ TD, 4) * 100)+ str("%"),
                                                                 str(round(test/ TD, 4) * 100)+ str("%"),
                                                                                           str(round(compatibility/ TD, 4) * 100)+ str("%"),
                                                                                                                              str(round(algorithm/ TD, 4) * 100)+ str("%"),
                                                                                                                                                             str(round(UNCHECKED/ TD, 4) * 100)+ str("%")
                            ]
                        ],
                        ignore_index=True)

                    # pd_proecessed_projects = pd_proecessed_projects.append(
                    #     [
                    #         [
                    #             tmpproject, "UNCHECKED debt", str(UNCHECKED), str(todo_UNCHECKED), str(fixme_UNCHECKED),
                    #             str(xxx_UNCHECKED), str(hack_UNCHECKED),
                    #             str(todo_UNCHECKED + fixme_UNCHECKED + xxx_UNCHECKED + hack_UNCHECKED)
                    #             , str(round(
                    #             (todo_UNCHECKED + fixme_UNCHECKED + xxx_UNCHECKED + hack_UNCHECKED) / UNCHECKED,
                    #             4) * 100) + str("%")
                    #         ]
                    #     ],
                    #     ignore_index=True)
                    #
                    # pd_proecessed_projects = pd_proecessed_projects.append(
                    #     [
                    #         [
                    #             tmpproject, "WITHOUT_SATD", str(WITHOUT_SATD), str(todo_WITHOUT_SATD),
                    #             str(fixme_WITHOUT_SATD),
                    #             str(xxx_WITHOUT_SATD), str(hack_WITHOUT_SATD),
                    #             str(todo_WITHOUT_SATD + fixme_WITHOUT_SATD + xxx_WITHOUT_SATD + hack_WITHOUT_SATD)
                    #             , str(round((
                    #                                     todo_WITHOUT_SATD + fixme_WITHOUT_SATD + xxx_WITHOUT_SATD + hack_WITHOUT_SATD) / WITHOUT_SATD,
                    #                         4) * 100) + str("%")
                    #         ]
                    #     ],
                    #     ignore_index=True)

                    pd_proecessed_projects.to_excel(".\\result\\td_propotion.xlsx", index=False)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # 项目列表,遍历所有项目提取注释。
    # projects_list=[]
    # for item in os.scandir("d:\\rawdataset"):
    #     if item.is_dir():
    #         print(item.name)
    #         Tokenizer(item.name,item.path)
    # 计算任务标签与SATD的关系
    # calTags()
    # 计算SATD所占的比例
    # calPropotionOfSATD()
    # 计算每一种技术债务在SATD中对比值
    cal_TD_propotion()










