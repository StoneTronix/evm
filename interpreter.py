from pathlib import Path
import struct
import sys
import yaml


cmd_info = {
    0x2A : [4, [0, 8, 24]],
    0xB9 : [5, [0, 8, 28]],
    0x65 : [3, [0, 8, 14]],
    0x13 : [3, [0, 8, 14]]
}


def interpret(binary_file_path, result_file_path, memory_range):
    filename = Path(binary_file_path).resolve()
    # Инициализация виртуальной памяти
    memory = [0] * 512
    register = [0] * 32

    with (open(filename, 'rb') as binary_file):
        filename = Path(result_file_path).resolve()
        log_file = open(filename, 'w')
        pc = 0

        while byte := binary_file.read(1):
            command = struct.unpack('B', byte)[0]

            # Обработка по командам
            if command == 0x2A:  # LOAD_CONST
                bytes = int.from_bytes(binary_file.read(3), byteorder='little')
                c = bytes >> 16
                b = bytes & 0x3FFF

                register[c] = b
            elif command == 0xB9:  # READ_MEM
                bytes = int.from_bytes(binary_file.read(4), byteorder='little')
                c = bytes >> 20
                b = bytes & 0xFFFFF

                register[c] = memory[b]
            elif command == 0x65:  # WRITE_MEM
                bytes = int.from_bytes(binary_file.read(2), byteorder='little')
                c = bytes >> 6
                b = bytes & 0x3F

                memory[register[c]] = register[b]
            elif command == 0x13:  # LESS_THAN
                bytes = int.from_bytes(binary_file.read(2), byteorder='little')
                c = bytes >> 6
                b = bytes & 0x3F

                memory[register[b]] = 1 if memory[register[b]] < register[c] else 0
            else:
                print(f"Unknown opcode at byte=:{pc}", file=sys.stderr)
                sys.exit(1)

            pc += 1

        yaml.dump(memory[memory_range[0]:memory_range[1]], log_file)
        return memory[memory_range[0]:memory_range[1]]


# interpret("program.bin", "result.yml", (0, 256))
# Командная строка
if __name__ == "__main__":
    interpret(sys.argv[1], sys.argv[2], (0, 256))  # диапазон памяти от 0 до 256