import argparse
from pathlib import Path
from ast_parser import AstParser
from clang.cindex import CompilationDatabase, CompilationDatabaseError
import glob
import multiprocessing
from random import shuffle


def files(input_path):
    file_types = ('*.c', '*.cc', '*.cpp')
    for file_type in file_types:
        for file_path in glob.glob(input_path + '**/' + file_type, recursive=True):
            yield file_path


class ParserProcess(multiprocessing.Process):
    def __init__(self, task_queue, max_contexts_num, input_path, output_path):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.parser = AstParser(max_contexts_num, output_path)
        try:
            self.compdb = CompilationDatabase.fromDirectory(input_path)
        except CompilationDatabaseError:
            self.compdb = None

    def run(self):
        default_compile_args = []

        while True:
            file_path = self.task_queue.get()
            if file_path is None:
                self.task_queue.task_done()
                break
            # print('Parsing : ' + file_path)
            if not self.compdb:
                # print('Compilation database was not found in the input directory, using default args list')
                self.parser.parse(file_path, default_compile_args)
            else:
                compile_args = self.compdb.getCompileCommands(file_path)
                # print('Compile flags : ' + str(compile_args))
                self.parser.parse(file_path, compile_args)
            self.task_queue.task_done()

        self.parser.save()
        return


def dump_data_set(samdump_data_setples, start, end, file_name):
    pass


def main():
    args_parser = argparse.ArgumentParser(
        description='cppminer generates a code2seq dataset from C++ sources')

    args_parser.add_argument('Path',
                             metavar='path',
                             type=str,
                             help='the path sources directory')

    args_parser.add_argument('OutPath',
                             metavar='out',
                             type=str,
                             help='the output path')

    args_parser.add_argument('-c', '--max_contexts_num',
                             metavar='MaxContextsPerSample',
                             type=int,
                             help='maximum number of contexts per sample',
                             default=100,
                             required=False)

    args_parser.add_argument('-p', '--processes_num',
                             metavar='ParallelProcessesNum',
                             type=int,
                             help='number of parallel processes',
                             default=4,
                             required=False)

    args = args_parser.parse_args()

    parallel_processes_num = args.processes_num
    print('Parallel processes num: ' + str(parallel_processes_num))

    max_contexts_num = args.max_contexts_num
    print('Max contexts num: ' + str(max_contexts_num))

    input_path = Path(args.Path).resolve().as_posix()
    print('Input path: ' + input_path)

    output_path = Path(args.OutPath).resolve().as_posix()
    print('Output path: ' + output_path)

    tasks = multiprocessing.JoinableQueue()
    processes = [ParserProcess(tasks, max_contexts_num, input_path, output_path)
                 for i in range(parallel_processes_num)]
    for p in processes:
        p.start()

    for file_path in files(input_path):
        tasks.put(file_path)

    # add terminating tasks
    for i in range(parallel_processes_num):
        tasks.put(None)

    # Wait for all of the tasks to finish
    tasks.join()
    for p in processes:
        p.join()

    # shuffle and merge samples
    files_map = dict()
    samples_list = []
    file_index = 0
    sample_index = 0
    for file_path in glob.glob(output_path + '**/*.c2s.num', recursive=True):
        with open(file_path) as file:
            samples_num = int(file.readline())

        files_map[file_index] = file_path[:-4]
        for _ in range(samples_num):
            samples_list.append((sample_index, file_index))
            sample_index += 1
        file_index += 1

    shuffle(samples_list)

    # split samples into test, validation and training parts
    all_samples_num = len(samples_list)
    train_samples_num = int(all_samples_num * 0.7)
    test_samples_num = (all_samples_num - train_samples_num) // 2

    dump_data_set(samples_list, 0, train_samples_num, "train.c2s")
    dump_data_set(samples_list, train_samples_num, train_samples_num + test_samples_num, "test.c2s")
    dump_data_set(samples_list, train_samples_num + test_samples_num, len(samples_list), "validation.c2s")


if __name__ == '__main__':
    main()
