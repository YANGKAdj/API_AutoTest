import yaml
import os

def read_yaml(file_name):
    #找到当前根目录，再拼接文件路径
    base_path = os.path.dirname(os.path.dirname(__file__))
    #根目录 + data +file_name
    file_path = os.path.join(base_path,"data",file_name)

    #读取
    with open(file_path,mode = 'r', encoding= 'utf-8') as f:
        return yaml.safe_load(f)

if __name__ == '__main__':
    print(read_yaml("test_data.yaml"))