import argparse
import xml.etree.ElementTree as ET
import struct


class Interpreter:
    def __init__(self):
        self.memory = [0] * 256  # 256 байт памяти
        self.accumulator = 0
        self.pc = 0  # Program Counter
        self.stack = []  # Стек
        self.instruction_limit = 1000

    def run(self, input_file, start_addr, end_addr, output_file):
        instruction_count = 0
        with open(input_file, "rb") as f:
            code = f.read()

        while self.pc < len(code):
            if instruction_count > self.instruction_limit:
                print("Превышен лимит инструкций. Возможно, программа зациклилась")
                break

            opcode_byte = struct.unpack(">B", code[self.pc : self.pc + 1])[0]
            opcode = opcode_byte & 0x1F  # Получаем код инструкции из младших 5 бит
            a_field = (opcode_byte >> 5) & 0x0F  # старшие 4 бита отбрасываем
            self.pc += 1

            if opcode == 0x01:  # CONST
                constant = struct.unpack(">H", code[self.pc : self.pc + 2])[0]
                self.stack.append(constant)
                self.pc += 2
            elif opcode == 0x02:  # LOAD
                addr = struct.unpack(">H", code[self.pc : self.pc + 2])[0]
                self.stack.append(self.memory[addr])
                self.pc += 2
            elif opcode == 0x03:  # STORE (не используется)
                if self.stack:
                    self.accumulator = self.stack.pop()
                else:
                    print("Error: stack is empty.")
                self.pc += 2

            elif opcode == 0x04:  # SHL
                shift = struct.unpack(">H", code[self.pc : self.pc + 2])[0]
                if self.stack:
                    value = self.stack.pop()
                    self.stack.append(value << shift)
                else:
                    print("Error: stack is empty.")
                self.pc += 2
            elif opcode == 0x05:  # OUTS
                if self.stack:
                    print(f"Output (stack): {self.stack[-1]}")
                else:
                    print("Error: stack is empty.")
                self.pc += 2  # Пропускаем 2 байта операнда
            elif opcode == 0x06:  # LOAD_ACC
                if self.stack:
                    self.accumulator = self.stack.pop()
                else:
                    print("Error: stack is empty.")
                self.pc += 2
            elif opcode == 0x07:  # STORE_ADDR
                if self.stack:
                    self.accumulator = self.stack.pop()
                else:
                    print("Error: stack is empty")
                self.pc += 2
            elif opcode == 0x08:  # STORE_VAL
                if self.stack:
                    value = self.stack.pop()
                    self.memory[self.accumulator] = value
                else:
                    print("Error: stack is empty")
                self.pc += 2

            else:
                raise ValueError(f"Invalid opcode: {opcode}")
            instruction_count += 1

        self.write_memory(start_addr, end_addr, output_file)

    def write_memory(self, start_addr, end_addr, output_file):
        root = ET.Element("memory")
        for addr in range(start_addr, end_addr + 1):
            mem_elem = ET.SubElement(root, "memory_cell")
            addr_elem = ET.SubElement(mem_elem, "address")
            addr_elem.text = str(addr)
            value_elem = ET.SubElement(mem_elem, "value")
            value_elem.text = str(self.memory[addr])

        tree = ET.ElementTree(root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interpreter for UVM.")
    parser.add_argument("input_file", help="Path to input binary file.")
    parser.add_argument("start_addr", type=int, help="Start address of memory range.")
    parser.add_argument("end_addr", type=int, help="End address of memory range.")
    parser.add_argument("output_file", help="Path to output XML file.")
    args = parser.parse_args()

    interpreter = Interpreter()
    try:
        interpreter.run(
            args.input_file, args.start_addr, args.end_addr, args.output_file
        )
        print("Execution finished successfully.")
    except Exception as e:
        print(f"Execution failed: {e}")
