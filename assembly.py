from pathlib import Path
import yaml
import sys

# Словарь для ассоциации имен команд с байт-кодами
translate = {
    'LOAD_CONST': 0x2A,  # Команда загрузки константы
    'READ_MEM': 0xB9,    # Команда чтения из памяти
    'WRITE_MEM': 0x65,   # Команда записи в память
    'LESS_THAN': 0x13    # Команда бинарной операции "<"
}
cmd_prefs = {
    0x2A : [4, [0, 8, 24]],
    0xB9 : [5, [0, 8, 28]],
    0x65 : [3, [0, 8, 14]],
    0x13 : [3, [0, 8, 14]]
}


def parse(line):
    parts = line.strip().split()
    args = [
        translate.get(parts[0]),
        int(parts[1]),
        int(parts[2])
    ]
    return args


def to_bytecode(args):
    bytecode = None
    a = args[0]  # Operation code
    cmd_info = cmd_prefs.get(args[0])  # Получение сведений, необходимых для формирования байт-кода

    if a is None:
        raise ValueError(f"Unknown command: {a}")
    else:
        command_size = cmd_info[0]
        byte_offsets = cmd_info[1]

        # Формирование частей команды при помощи масок
        b = args[1] << byte_offsets[1]
        c = (args[2]) << byte_offsets[2]

        bytecode = (a | b | c).to_bytes(command_size, 'little')
        return bytecode


def to_log(cmd_number, cmd_args, log_stream):
    record = {
        f'Parsed command #{cmd_number}' : {
            'A' : cmd_args[0],
            'B' : cmd_args[1],
            'C' : cmd_args[2],
        }
    }
    yaml.dump(record, log_stream, default_flow_style=False, allow_unicode=True)


def assembly(input_file_path, output_file_path, log_file_path = None):
    log_needed = False
    filename = ''

    if log_file_path is not None:    # Инициализация файла лога
        filename = Path(log_file_path).resolve()
        log_file = open(filename, 'w')
        log_needed = True

    name = Path(input_file_path).resolve()
    with (open(name, 'r') as file):
        output_file = open(output_file_path, 'wb')
        pc = 0

        for line in file:
            if line == '\n':
                continue
            parsed_args = parse(line)
            if log_needed:
                to_log(pc, parsed_args, log_file)
            bytecode = to_bytecode(parsed_args)
            output_file.write(bytecode)
            pc += 1
    return True


# assembly("program.asm", "program.bin", "log.yml")
# Командная строка
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: program <config_file>")
        sys.exit(1)
    assembly(sys.argv[1], sys.argv[2], sys.argv[3])