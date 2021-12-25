# coding=utf-8
import os
import sys
import prettytable as pt
import codecs

# 指定想要统计的文件类型
CPP_SUFFIX_SET = {'h', 'hpp', 'hxx', 'c', 'cpp', 'cc', 'cxx','go','rs','sol'}
PYTHON_SUFFIX_SET = {'py'}
JAVA_SUFFIX_SET = {'java'}

def list_files(project_path):
    # 遍历文件, 递归遍历文件夹中的所有
    filelists = []
    for parent, dirnames, filenames in os.walk(project_path):
        for filename in filenames:
            filelists.append(os.path.join(parent, filename))
    return filelists

def count_line(filename):
    # 统计一个文件的行数
    count = 0
    print(filename)
    with codecs.open(filename, 'r', 'utf-8') as f:
        for line in f.readlines():
            line = line.strip()  # 删除行首的空格
            if line != '' and line != '\n':   # 过滤掉空行
                if line[0] != '#' and line[0] != '/':  # 过滤掉注释行
                    count += 1
    return count

def statistics(filelist):
    cpp_lines = 0
    python_lines = 0
    java_lines = 0
    for filename in filelist:
        # print(filename)
        ext = filename.split('.')[-1]
        # print(ext)
        # if ext=="cpp":
        #     cpp_lines += count_line(filename)
        if ext in CPP_SUFFIX_SET:
            cpp_lines += count_line(filename)
            # print(cpp_lines)
        elif ext in PYTHON_SUFFIX_SET:
            python_lines += count_line(filename)
        elif ext in JAVA_SUFFIX_SET:
            java_lines += count_line(filename)
    total_lines = cpp_lines + python_lines + java_lines
    return cpp_lines, python_lines, java_lines, total_lines

def print_result(cpp_lines, python_lines, java_lines, total_lines):
    tb = pt.PrettyTable()
    tb.field_names = ['CPP', 'PYTHON', 'JAVA', 'TOTAL']
    tb.add_row([cpp_lines, python_lines, java_lines, total_lines])
    print(tb)


if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print("请指定项目路径!")
    # else:
    #     project_path = sys.argv[1]
    # filelists = list_files(".\\rawdataset\\")
    projects_list=[]
    for item in os.scandir(".\\rawdataset"):
        if item.is_dir():
            print(item.name)
            # projects_list.append(item.path)
            # Tokenizer(item.name,item.path)
            filelists = list_files(item.path)
            print_result(*statistics(filelists))

