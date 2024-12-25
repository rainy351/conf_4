import argparse
import xml.etree.ElementTree as ET
import struct


class Assembler:
    def __init__(self):
        self.opcodes = {
            "CONST": 0x01,
            "LOAD": 0x02,
            "STORE": 0x03,
            "SHL": 0x04,
            "OUTS": 0x05,
            "LOAD_ACC": 0x06,
            "STORE_ADDR": 0x07,
            "STORE_VAL": 0x08,
        }

    def assemble(self, input_file, output_file, log_file=None):
        assembled_code = b""
        log_entries = []
        address = 0

        with open(input_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                mnemonic = parts[0].upper()
                opcode = self.opcodes.get(mnemonic)

                if opcode is None:
                    raise ValueError(f"Invalid mnemonic: {mnemonic}")

                a_field = 0  # По умолчанию A = 0

                if mnemonic == "CONST":
                    constant = int(parts[1])
                    assembled_code += struct.pack(">B", opcode | (a_field << 5))
                    assembled_code += struct.pack(">H", constant)
                    log_entries.append(
                        {
                            "address": address,
                            "instruction": f"{mnemonic} {constant}",
                            "bytes": f"{opcode | (a_field << 5):02X}{constant:04X}",
                        }
                    )
                    address += 3
                elif mnemonic == "LOAD":
                    addr = int(parts[1])
                    assembled_code += struct.pack(">B", opcode | (a_field << 5))
                    assembled_code += struct.pack(">H", addr)
                    log_entries.append(
                        {
                            "address": address,
                            "instruction": f"{mnemonic} {addr}",
                            "bytes": f"{opcode | (a_field << 5):02X}{addr:04X}",
                        }
                    )
                    address += 3
                elif mnemonic == "STORE_ADDR":
                    assembled_code += struct.pack(">B", opcode | (a_field << 5))
                    assembled_code += struct.pack(
                        ">H", 0
                    )  # Пустое значение, т.к. операнд на стеке
                    log_entries.append(
                        {
                            "address": address,
                            "instruction": f"{mnemonic}",
                            "bytes": f"{opcode | (a_field << 5):02X}0000",
                        }
                    )
                    address += 3
                elif mnemonic == "STORE_VAL":
                    assembled_code += struct.pack(">B", opcode | (a_field << 5))
                    assembled_code += struct.pack(
                        ">H", 0
                    )  # Пустое значение, т.к. операнд на стеке
                    log_entries.append(
                        {
                            "address": address,
                            "instruction": f"{mnemonic}",
                            "bytes": f"{opcode | (a_field << 5):02X}0000",
                        }
                    )
                    address += 3
                elif mnemonic == "SHL":
                    shift = int(parts[1])
                    assembled_code += struct.pack(">B", opcode | (a_field << 5))
                    assembled_code += struct.pack(">H", shift)
                    log_entries.append(
                        {
                            "address": address,
                            "instruction": f"{mnemonic} {shift}",
                            "bytes": f"{opcode | (a_field << 5):02X}{shift:04X}",
                        }
                    )
                    address += 3
                elif mnemonic == "OUTS":
                    assembled_code += struct.pack(">B", opcode | (a_field << 5))
                    assembled_code += struct.pack(
                        ">H", 0
                    )  # Пустое значение, т.к. операнд на стеке
                    log_entries.append(
                        {
                            "address": address,
                            "instruction": f"{mnemonic}",
                            "bytes": f"{opcode | (a_field << 5):02X}0000",
                        }
                    )
                    address += 3
                elif mnemonic == "LOAD_ACC":
                    assembled_code += struct.pack(">B", opcode | (a_field << 5))
                    assembled_code += struct.pack(
                        ">H", 0
                    )  # Пустое значение, т.к. операнд на стеке
                    log_entries.append(
                        {
                            "address": address,
                            "instruction": f"{mnemonic}",
                            "bytes": f"{opcode | (a_field << 5):02X}0000",
                        }
                    )
                    address += 3

        with open(output_file, "wb") as f:
            f.write(assembled_code)

        if log_file:
            self.write_log(log_file, log_entries)

    def write_log(self, log_file, log_entries):
        root = ET.Element("log")
        for entry in log_entries:
            instruction_elem = ET.SubElement(root, "instruction")
            for key, value in entry.items():
                key_elem = ET.SubElement(instruction_elem, key)
                key_elem.text = str(value)

        tree = ET.ElementTree(root)
        tree.write(log_file, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assembler for UVM.")
    parser.add_argument("input_file", help="Path to input assembly file.")
    parser.add_argument("output_file", help="Path to output binary file.")
    parser.add_argument("--log_file", help="Path to log file.", default=None)
    args = parser.parse_args()

    assembler = Assembler()
    try:
        assembler.assemble(args.input_file, args.output_file, args.log_file)
        print("Assembly successful.")
    except Exception as e:
        print(f"Assembly failed: {e}")
