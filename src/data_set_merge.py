from pathlib import Path
from bitarray import bitarray
from tqdm import tqdm
import lmdb
import os
import random


class DataSetMerge:
    def __init__(self, output_path, map_size):
        self.output_path = output_path
        self.train_set_file = os.path.join(self.output_path, "dataset.train.c2s")
        self.test_set_file = os.path.join(self.output_path, "dataset.test.c2s")
        self.validation_set_file = os.path.join(self.output_path, "dataset.val.c2s")
        self.samples_db = lmdb.open(os.path.join(self.output_path, 'samples.db'), writemap=True)
        self.samples_db.set_mapsize(map_size)
        self.total_num = 0

    def merge(self, clear_resources=True):
        functions = set()
        sample_id = 0
        self.total_num = 0
        with self.samples_db.begin(write=True) as txn:
            files_num = sum(1 for _ in Path(self.output_path).rglob('*.c2s'))
            with tqdm(total=files_num) as pbar:
                for file_path in Path(self.output_path).rglob('*.c2s'):
                    with file_path.open() as file:
                        # print('Loading file: ' + file_path.absolute().as_posix())
                        for line in file.readlines():
                            src_mark_str, _, sample_line = line.partition(')')
                            src_mark = src_mark_str[2:]
                            if src_mark not in functions:
                                txn.put(str(sample_id).encode('ascii'), sample_line.encode('ascii'))
                                sample_id += 1
                                functions.add(src_mark)
                    if clear_resources:
                        os.remove(file_path.absolute().as_posix())
                    pbar.update(1)
            self.total_num = sample_id - 1

    def dump_datasets(self, train_set_ratio=0.7):
        # split samples into test, validation and training parts
        all_samples_num = self.total_num + 1
        train_samples_num = int(all_samples_num * train_set_ratio)
        test_samples_num = (all_samples_num - train_samples_num) // 2
        processed = bitarray(all_samples_num)
        processed.setall(False)
        train_file = open(self.train_set_file, 'w')
        train_index = 0
        test_file = open(self.test_set_file, 'w')
        test_index = 0
        validation_file = open(self.validation_set_file, 'w')
        validation_index = 0
        try:
            with self.samples_db.begin(write=False) as txn:
                for _ in tqdm(range(self.total_num + 1)):
                    index = random.randint(0, self.total_num)
                    while processed[index]:
                        index = random.randint(0, self.total_num)
                    processed[index] = True
                    sample = txn.get(str(index).encode('ascii'))
                    if train_index < train_samples_num:
                        train_file.write(sample.decode('ascii'))
                        train_index += 1
                    elif test_index < test_samples_num:
                        test_file.write(sample.decode('ascii'))
                        test_index += 1
                    elif validation_index < test_samples_num:
                        validation_file.write(sample.decode('ascii'))
                        validation_index += 1
        finally:
            print("Closing files ...")
            train_file.close()
            test_file.close()
            validation_file.close()
