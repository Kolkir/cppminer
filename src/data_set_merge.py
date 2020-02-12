import glob
from random import shuffle
import os


class DataSetMerge:
    def __init__(self, output_path):
        self.files_map = dict()
        self.samples_list = []
        self.output_path = output_path
        self.train_set_file = os.path.join(self.output_path, "train.c2s")
        self.test_set_file = os.path.join(self.output_path, "test.c2s")
        self.validation_set_file = os.path.join(self.output_path, "validation.c2s")

    def read_samples(self):
        file_index = 0
        for file_path in glob.glob(self.output_path + '**/*.c2s.num', recursive=True):
            self.files_map[file_index] = file_path[:-4]
            with open(file_path) as file:
                for line in file.readlines():
                    sample_pos = int(line)
                    self.samples_list.append((sample_pos, file_index))
            file_index += 1

    def shuffle_samples(self):
        shuffle(self.samples_list)

    def merge(self, train_set_ratio=0.7):
        # split samples into test, validation and training parts
        all_samples_num = len(self.samples_list)
        train_samples_num = int(all_samples_num * train_set_ratio)
        test_samples_num = (all_samples_num - train_samples_num) // 2

        self.dump_data_set(0, train_samples_num, self.train_set_file)
        self.dump_data_set(train_samples_num, train_samples_num + test_samples_num,
                           self.test_set_file)
        self.dump_data_set(train_samples_num + test_samples_num, all_samples_num,
                           self.validation_set_file)

    def clear(self):
        files_to_hold = [self.train_set_file, self.test_set_file, self.validation_set_file]
        files = list(glob.glob(self.output_path + '**/*.*', recursive=True))
        for file_path in files:
            if file_path not in files_to_hold:
                os.remove(file_path)

    def dump_data_set(self, start, end, file_name):
        files_cache = dict()
        with open(file_name, "w") as output_file:
            for i in range(start, end):
                sample_pos, file_index = self.samples_list[i]
                if file_index in files_cache.keys():
                    samples_file = files_cache[file_index]
                else:
                    samples_file = open(self.files_map[file_index], "r")
                    files_cache[file_index] = samples_file
                samples_file.seek(sample_pos)
                sample = samples_file.readline()
                output_file.write(sample)

        for _, file in files_cache.items():
            file.close()
