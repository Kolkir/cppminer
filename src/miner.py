import argparse
from pathlib import Path
from ast_parser import AstParser
from clang.cindex import CompilationDatabase, CompilationDatabaseError
import glob
import multiprocessing
from data_set_merge import DataSetMerge


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

    print("Parsing files ...")
    for file_path in files(input_path):
        tasks.put(file_path)

    # add terminating tasks
    for i in range(parallel_processes_num):
        tasks.put(None)

    # Wait for all of the tasks to finish
    tasks.join()
    for p in processes:
        p.join()
    print("Parsing done")

    # shuffle and merge samples
    print("Merging datasets ...")
    merge = DataSetMerge(output_path)
    print("Reading samples ...")
    merge.read_samples()
    print("Shuffling samples ...")
    merge.shuffle_samples()
    print("Merging samples ...")
    merge.merge(0.7)
    print("Clearing ...")
    merge.clear()
    print("Merging done")


if __name__ == '__main__':
    main()
