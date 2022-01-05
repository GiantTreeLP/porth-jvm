#!/usr/bin/env python3
import os
import sys
from os import path
from typing import Optional

from jvm.generator import generate_jvm_bytecode
from porth.porth import usage, Program, ParseContext, parse_program_from_file, type_check_program, \
    PORTH_EXT, cmd_call_echoed


def main():
    argv = sys.argv
    assert len(argv) >= 1
    compiler_name, *argv = argv

    include_paths = ['.', './std/']
    unsafe = False

    while len(argv) > 0:
        if argv[0] == '-debug':
            argv = argv[1:]
            debug = True
        elif argv[0] == '-I':
            argv = argv[1:]
            if len(argv) == 0:
                usage(compiler_name)
                print("[ERROR] no path is provided for `-I` flag", file=sys.stderr)
                exit(1)
            include_path, *argv = argv
            include_paths.append(include_path)
        elif argv[0] == '-unsafe':
            argv = argv[1:]
            unsafe = True
        else:
            break

    if len(argv) < 1:
        usage(compiler_name)
        print("[ERROR] no subcommand is provided", file=sys.stderr)
        exit(1)
    subcommand, *argv = argv

    program_path: Optional[str] = None
    program: Program

    if subcommand == "check":
        if len(argv) < 1:
            usage(compiler_name)
            print("[ERROR] no input file is provided for the checking", file=sys.stderr)
            exit(1)
        program_path, *argv = argv
        include_paths.append(path.dirname(program_path))
        parse_context = ParseContext()
        parse_program_from_file(parse_context, program_path, include_paths)
        program = Program(ops=parse_context.ops, memory_capacity=parse_context.memory_capacity)
        proc_contracts = {proc.addr: proc.contract for proc in parse_context.procs.values()}
        if not unsafe:
            type_check_program(program, proc_contracts)
    elif subcommand == "com":
        silent = False
        run = False
        output_path = None
        while len(argv) > 0:
            arg, *argv = argv
            if arg == '-r':
                run = True
            elif arg == '-s':
                silent = True
            elif arg == '-o':
                if len(argv) == 0:
                    usage(compiler_name)
                    print("[ERROR] no argument is provided for parameter -o", file=sys.stderr)
                    exit(1)
                output_path, *argv = argv
            else:
                program_path = arg
                break

        if program_path is None:
            usage(compiler_name)
            print("[ERROR] no input file is provided for the compilation", file=sys.stderr)
            exit(1)

        basename: str
        basedir: str
        if output_path is not None:
            if path.isdir(output_path):
                basename = path.basename(program_path)
                if basename.endswith(PORTH_EXT):
                    basename = basename[:-len(PORTH_EXT)]
                basedir = path.dirname(output_path)
            else:
                basename = path.basename(output_path)
                basedir = path.dirname(output_path)
        else:
            basename = path.basename(program_path)
            if basename.endswith(PORTH_EXT):
                basename = basename[:-len(PORTH_EXT)]
            basedir = path.dirname(program_path)

        # if basedir is empty we should "fix" the path appending the current working directory.
        # So we avoid `com -r` to run command from $PATH.
        if basedir == "":
            basedir = os.getcwd()
        basepath = path.join(basedir, basename)

        include_paths.append(path.dirname(program_path))

        parse_context = ParseContext()
        parse_program_from_file(parse_context, program_path, include_paths)
        program = Program(ops=parse_context.ops, memory_capacity=parse_context.memory_capacity)
        if not unsafe:
            type_check_program(program, {proc.addr: proc for proc in parse_context.procs.values()})
        if not silent:
            print("[INFO] Generating %s" % (basepath + ".class"))
        generate_jvm_bytecode(parse_context, program, "Main.class", program_path)
        cmd_call_echoed(["javap", "-v", "-c", "-constants", "Main.class"], silent)
        if run:
            # -Xverify:none to disable verification of stack map frames
            exit(cmd_call_echoed(["java", "-Xverify:none", "Main"] + argv, silent))
    elif subcommand == "help":
        usage(compiler_name)
        exit(0)
    else:
        usage(compiler_name)
        print("[ERROR] unknown subcommand %s" % subcommand, file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()
