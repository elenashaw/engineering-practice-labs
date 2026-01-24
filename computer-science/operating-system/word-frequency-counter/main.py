import os   
import threading 

def get_segments(file_path,n):
    """
    :param file_path: 文本文件路径
    :param n: 线程数
    :return: 返回一个包含n个元组的列表，每个元组表示文本文件的分段坐标(起始位置，结束位置)
    该函数将文本文件大致均分为n个部分，并确保每个部分在换行符或空格处结束，以避免在单词中间断开。
    例如，假设文本文件内容为 "Hello World\nThis is a test file."，文件大小为30字节，n=3，则函数可能返回以下分段坐标：
    [(0, 12), (12, 22), (22, 30)]
    这表示第一个分段包含 "Hello World\n"，第二个分段包含 "This is a "，第三个分段包含 "test file."。
    这样分段可以确保每个部分在单词边界处结束，避免在单词中间断开。
    """

    # 获取本文文件的字节大小(总长度)
    file_size = os.path.getsize(file_path)   

    #获取每个分块的大小
    chunk_size = file_size // n 

    # 创建一个用于记录分段坐标的空列表             
    segments = []                                         

    # 上一个人的终点位置，[)
    last_pos = 0

    # 找到合适的分段位置(分段加微调)
    with open(file_path, 'rb') as f:
        for i in range(n):
            # 计算当前分块的结束位置
            if i == n - 1:

                # 最后一个分块直接到文件末尾
                segments.append((last_pos, file_size))
                break
            else:
                # 移动到预定的分块结束位置
                f.seek(last_pos + chunk_size)
                
                # 读取到下一个换行符的位置
                while True:

                    # 逐个字节读取，直到遇到换行符或者空格
                    byte = f.read(1) 
                    if not byte or byte == b'\n' or byte == b' ':
                        break

                # 记录当前分块的结束位置
                end_pos = f.tell()

                # 保存当前分块的起始和结束位置
                segments.append((last_pos, end_pos))

                # 更新上一个分块的结束位置
                last_pos = end_pos
    return segments




def count_words_in_chunk(file_path, start, end, result_dict, index):
    # 线程维护自己的词典
        # 为什么要传入result_dict和index？方便后期直接按照索引遍历维护，不至于手动调用
        # 线程不可以返回值
    local_dic = {}
    with open(file_path, 'rb') as f:
        # 切换到指定的起始位置
        f.seek(start)
        # 读取指定范围内的内容
        chunk=f.read(end - start)

        # 将二进制内容解码为字符串
        text = chunk.decode('utf-8', errors='ignore')

        # 使用空白字符分割文本并计算单词数
        words = text.split()   

        for word in words:
            # 数据清洗：转为小写；移除字符串首尾指定的字符
            clean_word = word.lower().strip('.,!?";:()[]{}<>')

            # 由于使用了strip,需要确保不是空字符串
            if clean_word:  
                local_dic[clean_word] = local_dic.get(clean_word, 0) + 1

    # 将本地词典存入共享结果字典
    result_dict[index] = local_dic






def main(file_path, n_threads):
    # 获取文件的分段坐标
    segments = get_segments(file_path, n_threads)

    # 创建一个列表用于维护线程数据结构
    results=[None] * n_threads
    #可以写成比较好理解的形式
    # results = [{} for _ in range(n_threads)]


    # 维护线程，以防丢失
    threads = []

    for i in range(n_threads):
        start, end = segments[i]
        t = threading.Thread(
            target=count_words_in_chunk, 
            args=(file_path, start, end, results, i)
            )
        # 存进线程列表
        threads.append(t)
        # 启动线程
        t.start()

    # 等待所有线程完成
    for t in threads:
        #  barrier屏障同步机制，等待所有线程完成后再继续
        t.join()

    # 合并所有线程的结果
    final_result = {}
    for local_dic in results:
        for word, count in local_dic.items():
            # 合并词频统计结果
            final_result[word] = final_result.get(word, 0) + count

    # 打印最终的词频统计结果
    sorted_items = sorted(final_result.items(), key=lambda x: x[1], reverse=True)
    for word, count in sorted_items[:10]: # 只取前10个
        print(f"{word}: {count}")

    




if __name__ == "__main__":
    file_path = 'sample.txt' 
    n_threads = 4         
    main(file_path, n_threads)