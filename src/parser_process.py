import multiprocessing
import os
from clang.cindex import CompilationDatabase, CompilationDatabaseError
from cpp_parser import AstParser


def is_object_file(file_path):
    file_name = os.path.basename(file_path)
    if '.o.' in file_name:
        return True
    elif '.o' in file_name[-2:]:
        return True
    else:
        return False


class ParserProcess(multiprocessing.Process):
    def __init__(self, task_queue, max_contexts_num, max_path_len, max_subtokens_num, max_ast_depth, input_path, output_path):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.parser = AstParser(max_contexts_num, max_path_len, max_subtokens_num, max_ast_depth, output_path)
        try:
            self.compdb = CompilationDatabase.fromDirectory(input_path)
        except CompilationDatabaseError:
            self.compdb = None

    def run(self):
        default_compile_args = []

        while self.parse_file(default_compile_args):
            pass

        self.save()
        return

    def save(self):
        self.parser.save()

    def parse_file(self, default_compile_args=[]):
        file_path = self.task_queue.get()
        if file_path is None:
            self.task_queue.task_done()
            return False
        # print('Parsing : {0} [{1}]'.format(file_path, os.getpid()))
        if not self.compdb:
            # print('Compilation database was not found in the input directory, using default args list')
            self.parser.parse([file_path] + default_compile_args)
        else:
            commands = self.compdb.getCompileCommands(file_path)
            if commands and len(commands) > 0:
                command = commands[0]
                cwd = os.getcwd()
                os.chdir(command.directory)
                args = []
                cmd_args = command.arguments
                next(cmd_args)  # drop compiler executable path
                for arg in cmd_args:
                    if arg == '-Xclang':
                        next(cmd_args)  # skip clang specific arguments
                    elif arg == '-c':
                        continue  # drop input filename option
                    elif arg == '-o':
                        continue  # drop output filename option
                    elif os.path.isfile(arg) or os.path.isdir(arg):
                        continue  # drop file names
                    elif is_object_file(arg):
                        continue  # drop file names
                    else:
                        args.append(arg)
                self.parser.parse(args, command.filename)
                os.chdir(cwd)
        self.task_queue.task_done()
        return True
