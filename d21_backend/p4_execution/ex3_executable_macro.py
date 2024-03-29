import random
from copy import copy
from typing import Optional

from d21_backend.config import config
from d21_backend.p1_utils.canned import UI2CNN
from d21_backend.p1_utils.data_type import DataType, Register
from d21_backend.p1_utils.errors import HeapaExecutionError, RegisterInvalidError, DumpExecutionError, MhinfExecutionError, \
    PrimaExecutionError, McpckExecutionError, SegmentNotFoundError, NotImplementedExecutionError, \
    UserDefinedMacroExecutionError, TPFServerMemoryError, UcdrError
from d21_backend.p1_utils.ucdr import pars_to_date, date_to_pars
from d21_backend.p2_assembly.mac2_data_macro import get_macros
from d21_backend.p2_assembly.seg2_ins_operand import FieldBaseDsp
from d21_backend.p2_assembly.seg5_exec_macro import KeyValue, SegmentCall
from d21_backend.p3_db.pnr import PnrLocator
from d21_backend.p4_execution.ex1_state import State


class RealTimeMacro(State):
    def getcc(self, node: KeyValue) -> str:
        address = self.vm.allocate()
        self._core_block(address, node.keys[0], node.keys[1])
        self.regs.R14 = address
        return node.fall_down

    def alasc(self, node: KeyValue) -> str:
        address = self.vm.allocate()
        self.vm.set_value(self.regs.get_value("R7"), address + 8)
        self.regs.set_value(address + 8, "R7")
        ce1aut = self.regs.get_value("R9") + get_macros()["EB0EB"].evaluate("CE1AUT")
        self.vm.set_value(address, ce1aut)
        return node.fall_down

    def levta(self, node: KeyValue) -> str:
        level = node.get_value("LEVEL")
        in_use = node.get_value("INUSE") if node.get_value("INUSE") else node.fall_down
        not_used = node.get_value("NOTUSED") if node.get_value("NOTUSED") else node.fall_down
        return in_use if self._is_level_present(level) else not_used

    def crusa(self, node: KeyValue) -> str:
        for index in range(16):
            level = node.get_value(f"S{index}")
            if level is None:
                break
            control_address = self.get_ecb_address(f"D{level}", "CE1CT")
            size_address = self.get_ecb_address(f"D{level}", "CE1CC")
            self.vm.set_value(0x01, control_address, 2)
            self.vm.set_value(0, size_address, 2)
        return node.fall_down

    def detac(self, node: KeyValue) -> str:
        level = node.keys[0]
        core_address = self.get_ecb_address(level, "CE1CR")
        file_address = self.get_ecb_address(level, "CE1FA")
        core_bytes = self.vm.get_bytes(core_address, 8)
        file_bytes = self.vm.get_bytes(file_address, 8)
        self.detac_stack[level[1]].append((core_bytes, file_bytes))
        return node.fall_down

    def attac(self, node: KeyValue) -> str:
        level = node.keys[0]
        core_address = self.get_ecb_address(level, "CE1CR")
        file_address = self.get_ecb_address(level, "CE1FA")
        core_bytes, file_bytes = self.detac_stack[level[1]].pop()
        self.vm.set_bytes(core_bytes, core_address, len(core_bytes))
        self.vm.set_bytes(file_bytes, file_address, len(file_bytes))
        return node.fall_down

    def flipc(self, node: KeyValue) -> str:
        level1: str = node.keys[0]
        level2: str = node.keys[1]
        core_address1 = self.get_ecb_address(level1, "CE1CR")
        file_address1 = self.get_ecb_address(level1, "CE1FA")
        core_address2 = self.get_ecb_address(level2, "CE1CR")
        file_address2 = self.get_ecb_address(level2, "CE1FA")
        core_bytes1 = self.vm.get_bytes(core_address1, 8)
        file_bytes1 = self.vm.get_bytes(file_address1, 8)
        core_bytes2 = self.vm.get_bytes(core_address2, 8)
        file_bytes2 = self.vm.get_bytes(file_address2, 8)
        self.vm.set_bytes(core_bytes1, core_address2, len(core_bytes1))
        self.vm.set_bytes(file_bytes1, file_address2, len(file_bytes1))
        self.vm.set_bytes(core_bytes2, core_address1, len(core_bytes2))
        self.vm.set_bytes(file_bytes2, file_address1, len(file_bytes2))
        return node.fall_down

    def senda(self, node: KeyValue) -> str:
        message: str = node.get_value("MSG")
        if message:
            self.messages.append(message.replace("'", ""))
            return node.fall_down
        can: str = node.get_value("CAN")
        if not can:
            raise UserDefinedMacroExecutionError(node)
        canned_number = get_macros()["UI2PF"].evaluate(can)
        if node.get_value("SEC") == "YES":
            canned_number += 256
        message_string = next((canned["message"] for canned in UI2CNN
                               if int(canned["number"]) == canned_number), None)
        if not message_string:
            raise UserDefinedMacroExecutionError(node)
        self.messages.append(message_string)
        return node.fall_down

    def sysra(self, node: KeyValue) -> Optional[str]:
        return_code = node.get_value("P1")
        dump = node.get_value("P2")
        self.dumps.append(dump)
        if return_code == "R":
            return node.fall_down
        elif return_code == "E":
            return None
        else:
            raise DumpExecutionError

    def serrc(self, node: KeyValue) -> Optional[str]:
        return_code = node.keys[0]
        dump = node.keys[1]
        self.dumps.append(dump)
        if return_code == "R":
            return node.fall_down
        elif return_code == "E":
            return None
        else:
            raise DumpExecutionError

    def snapc(self, node: KeyValue) -> str:
        dump = node.keys[1]
        if len(dump) != 6:
            raise DumpExecutionError(node)
        self.dumps.append(dump)
        return node.fall_down

    def entrc(self, node: SegmentCall) -> Optional[str]:
        called_seg: str = node.keys[0]
        if called_seg in self.stop_segments:
            return None
        self.fields["CE3ENTPGM"] = DataType("C", input=self.seg.name).to_bytes()
        self.call_stack.append((node.fall_down, self.seg.name))
        self._init_seg(called_seg)
        return node.goes

    def entnc(self, node: SegmentCall) -> Optional[str]:
        called_seg: str = node.keys[0]
        if called_seg in self.stop_segments:
            return None
        self.fields["CE3ENTPGM"] = DataType("C", input=self.seg.name).to_bytes()
        self._init_seg(called_seg)
        return node.goes

    def entdc(self, node: SegmentCall) -> Optional[str]:
        called_seg: str = node.keys[0]
        if called_seg in self.stop_segments:
            return None
        self.fields["CE3ENTPGM"] = DataType("C", input=self.seg.name).to_bytes()
        del self.call_stack[:]
        self._init_seg(called_seg)
        return node.goes

    def backc(self, node) -> str:
        try:
            branch, seg_name = self.call_stack.pop()
        except IndexError:
            raise SegmentNotFoundError(node)
        self._init_seg(seg_name)
        return branch

    def maloc(self, node: KeyValue) -> str:
        size_reg: str = node.get_value("SIZE") if node.command == "MALOC" else node.get_value("COUNT")
        reg: Register = Register(size_reg)
        if not reg.is_valid():
            raise UserDefinedMacroExecutionError(node)
        self.regs.set_value(self.vm.allocate(), reg)
        return node.fall_down

    def pnamc(self, node: KeyValue) -> str:
        name_type = node.get_value("NAMETYPE")
        current_seg = DataType("C", input=self.seg.seg_name).to_bytes()
        seg_bytes = self.fields["CE3ENTPGM"] if name_type in {"CALLER", "ENTER"} else current_seg
        field: FieldBaseDsp = node.get_value("FIELD")
        self.vm.set_bytes(seg_bytes, self.regs.get_value(field.base) + field.dsp, 4)
        return node.fall_down

    def cinfc(self, node: KeyValue) -> str:
        reg_arg: str = node.get_value("REG")
        reg: Register = Register(reg_arg)
        if not reg.is_valid():
            raise UserDefinedMacroExecutionError(node)
        self.regs.set_value(0, reg)
        return node.fall_down


class UserDefinedMacro(State):

    @staticmethod
    def realtima(node: KeyValue) -> str:
        realtime_label = node.get_value("YES") if node.get_value("YES") else node.fall_down
        return realtime_label

    def aaget(self, node: KeyValue) -> str:
        address = self.vm.allocate()
        ecb_address = self.get_ecb_address("D1", "CE1CR")
        self.vm.set_value(address, ecb_address)
        reg = Register(node.get_value("BASEREG"))
        if reg.is_valid():
            self.regs.set_value(address, reg)
        return node.fall_down

    def aacpy(self, node: KeyValue) -> str:
        to_level = node.get_value("TO")
        if to_level not in config.ECB_LEVELS or to_level == "1":
            raise UserDefinedMacroExecutionError(node)
        core_reference = self.get_ecb_address(f"D{to_level}", "CE1CR")
        aaa_copy = self.vm.allocate()
        self.vm.set_value(aaa_copy, core_reference)
        aaa_bytes = copy(self.vm.frames[self.vm.base_key(self.aaa_address)])
        self.vm.set_bytes(aaa_bytes, aaa_copy, len(aaa_bytes))
        return node.fall_down

    def aaint(self, node: KeyValue) -> str:
        if not node.get_value("INIT"):
            return node.fall_down
        self.vm.set_frame(bytearray(), self.aaa_address)
        return node.fall_down

    def heapa(self, node: KeyValue) -> str:
        # REG, REF and SREF
        reg = Register(node.get_value("REG"))
        ref = node.get_value("REF")
        if ref is None:
            sref = node.get_value("SREF")
            if sref is None:
                raise HeapaExecutionError
            ref_bytes = self.seg.get_constant_bytes(sref, 8)
            ref = DataType("X", bytes=ref_bytes).decode

        # ERROR= for forced errors
        error_label = node.get_value("ERROR")
        if error_label and self.is_error(node.label):
            if reg.is_valid():
                self.regs.set_value(0, reg)
            return error_label

        # HEAPA / CFCMA / EHEAPA command types
        command = node.keys[0]
        heap = self.heap["new"] if node.command == "EHEAPA" else self.heap["old"]
        if command == "ALLOCATE":
            address = self.vm.allocate()
            heap[ref] = address
            if reg.is_valid():
                self.regs.set_value(address, reg)
        elif command == "LOADADD":
            address = heap[ref] if ref in heap else 0
            if reg.is_valid():
                self.regs.set_value(address, reg)
            if address == 0 and error_label:
                return error_label
        elif command == "FREE":
            heap.pop(ref, None)
        else:
            raise HeapaExecutionError
        return node.fall_down

    def mhinf(self, node: KeyValue) -> str:
        if node.keys[0] != "ECB":
            raise MhinfExecutionError
        reg = Register(node.get_value("REG"))
        if not reg.is_valid():
            raise MhinfExecutionError
        option = node.get_value("INPTR")
        if option == "NAME":
            airline_code = self.vm.get_bytes(self.regs.get_value(reg), 2)
            self.set_partition(DataType("X", bytes=airline_code).decode)
        else:
            raise MhinfExecutionError
        return node.fall_down

    def mcpck(self, node: KeyValue) -> str:
        match_label = node.get_value("YES") if node.get_value("YES") else node.fall_down
        not_match_label = node.get_value("NO") if node.get_value("NO") else node.fall_down
        if node.get_value("GROUP") == "LAN":
            return match_label if self.get_partition() in {"LA", "4M", "XL"} else not_match_label
        if node.get_value("PP"):
            not_mcp_label = node.get_value("NOTMCP")
            if not_mcp_label and self.get_partition() not in {"LA", "4M", "XL"}:
                return not_mcp_label
            return match_label if self.get_partition() in {"LA"} else not_match_label
        if node.get_value("NO"):
            return match_label if self.get_partition() in {"LA", "4M", "XL"} else not_match_label
        raise McpckExecutionError

    @staticmethod
    def nmsea(node: KeyValue) -> str:
        # TODO Finish NMSEA when data on NM0ID or WGL1 is available
        error = node.get_value("ERROR")
        return error if error else node.fall_down

    @staticmethod
    def tkdna(node: KeyValue) -> str:
        error = node.get_value("ERROR")
        if not error:
            raise NotImplementedExecutionError
        return error

    @staticmethod
    def toura(node: KeyValue) -> str:
        inhibit = node.get_value("INHIBIT")
        if inhibit:
            return inhibit
        return node.fall_down

    def prima(self, node: KeyValue) -> str:
        if "PNR" not in node.keys and "AAA" not in node.keys:
            raise PrimaExecutionError
        if node.get_value("MODE") != "CHECK":
            raise PrimaExecutionError
        if node.get_value("PNRLEV") or node.get_value("PRDATA"):
            raise PrimaExecutionError
        match_label = node.get_value("YES") if node.get_value("YES") else node.fall_down
        not_match_label = node.get_value("NO") if node.get_value("NO") else node.fall_down
        prime_host = self.vm.get_value(self.aaa_address + get_macros()["WA0AA"].evaluate("WA0PHA"), 1) & 0x0F
        input_type = node.get_value("PH")
        if prime_host == 0:
            return not_match_label
        elif prime_host == 2:
            return match_label if input_type in ("1F", "ANY") else not_match_label
        elif prime_host == 3:
            return match_label if input_type in ("1B", "ANY") else not_match_label
        else:
            raise PrimaExecutionError

    def pnrcc(self, node: KeyValue) -> str:
        action = node.get_value("ACTION")
        reg = Register(node.get_value("REG"))
        if not reg.is_valid():
            raise RegisterInvalidError
        pnrcm_base = self.regs.get_value(reg)
        self.seg.load_macro("PNRCM")
        if self.is_error(node.label):
            error_code = self.seg.evaluate("#PM1ER5")
            self.vm.set_value(error_code, pnrcm_base + self.seg.evaluate("PM1ERR"), 1)
            return node.fall_down
        if action in ["CRLON"]:
            pnr_locator_bytes = self.vm.get_bytes(pnrcm_base + self.seg.evaluate("PM1LOC"), 6)
            pnr_locator = DataType("X", bytes=pnr_locator_bytes).decode
            ordinal = PnrLocator.to_ordinal(pnr_locator)
            self.vm.set_value(ordinal, pnrcm_base + self.seg.evaluate("PM1ORN"))
            self.vm.set_value(ordinal, pnrcm_base + self.seg.evaluate("PM1FAD"))
        return node.fall_down

    def pnrua(self, node: KeyValue) -> str:
        # Ensure PNRUA always return an error by setting R0 to 1
        self.regs.set_value(1, "R0")
        return node.fall_down

    def date_macro(self, node: KeyValue) -> str:
        pars_reg: str = node.get_value("PARS")
        if not pars_reg or not Register(pars_reg).is_valid():
            raise UcdrError
        pars_value: int = self.regs.get_value(pars_reg)
        pars_bytes: bytearray = pars_to_date(pars_value, full_year=True)
        field: FieldBaseDsp = node.get_value("OK")
        address: int = self.regs.get_value(field.base.reg) + field.dsp
        self.vm.set_bytes(pars_bytes, address, len(pars_bytes))
        return node.fall_down

    def pars_date(self, node: KeyValue) -> str:
        # Get the option_byte and do the conversion
        option_byte = self.vm.get_byte(self.regs.R6)
        if option_byte == 0x00:
            # Date to PARS day number. 03OCT (2019) -> 4CB0
            date_bytes = self.vm.get_bytes(self.regs.R7, 5)
            try:
                days_from_start, days_from_today = date_to_pars(date_bytes)
                self.regs.R6 = days_from_start
                self.regs.R7 = days_from_today
            except ValueError:
                self.regs.R6 = 0
        elif option_byte == 0xFF:
            # PARS day number to Date. 4CB0 -> 03OCT
            days_from_start = self.regs.R7
            try:
                date_bytes = pars_to_date(days_from_start)
                self.regs.R7 = self.regs.R6
                self.vm.set_bytes(date_bytes, self.regs.R7, len(date_bytes))
            except ValueError:
                self.regs.R6 = 0
        else:
            self.regs.R6 = 0
        return node.fall_down

    def generate_locator(self, node: KeyValue) -> str:
        r6: int = self.regs.get_value("R6")
        ul4loc: int = r6 + get_macros()["UL0LC"].evaluate("UL4LOC")
        ul4ord: int = r6 + get_macros()["UL0LC"].evaluate("UL4ORD")
        ordinal: int = random.randint(0, 26 ** 6)
        locator: str = PnrLocator.to_locator(ordinal)
        locator_bytes: bytearray = DataType("C", input=locator).to_bytes()
        self.vm.set_value(ordinal, ul4ord)
        self.vm.set_bytes(locator_bytes, ul4loc, len(locator))
        return node.fall_down

    def uio1_user_exit(self, node: KeyValue) -> str:
        macros = get_macros()
        r2 = self.regs.get_value("R2")
        if r2 != 0:
            ui2cnn = r2 + macros["UI2PF"].lookup("UI2CNN").dsp
            ui2uio = r2 + macros["UI2PF"].lookup("UI2UIO").dsp
            canned_number = self.vm.get_unsigned_value(ui2cnn, 1)
            if self.vm.all_bits_on(ui2uio, 0x01):  # UI2SEC = 0x01
                canned_number += 256
            message_string = next((canned["message"] for canned in UI2CNN
                                   if int(canned["number"]) == canned_number), None)
            if not message_string:
                raise UserDefinedMacroExecutionError(node)
            self.messages.append(message_string)
            return node.fall_down
        ebw000_address: int = self.regs.get_value("R9") + macros["EB0EB"].evaluate("EBW000")
        ebw000: bytearray = self.vm.get_bytes(ebw000_address, 72)
        eom = DataType("C", input="+").to_bytes()[0]
        if not any(eom == byte for byte in ebw000):
            raise UserDefinedMacroExecutionError(node)
        message: bytearray = bytearray()
        for byte in ebw000:
            if byte == eom:
                break
            message.append(byte)
        message_string = DataType("X", bytes=message).decode
        self.messages.append(message_string)
        return node.fall_down

    def fmsg_user_exit(self, node: KeyValue) -> str:
        r1 = self.regs.get_value("R1")
        r2 = self.regs.get_value("R2")
        if not r1 or not r2:
            raise TPFServerMemoryError
        ui2bct = r2 + get_macros()["UI2PF"].lookup("UI2BCT").dsp
        length = self.vm.get_value(ui2bct, 2)
        if not length:
            return node.fall_down
        message_bytes = self.vm.get_bytes(r1, length)
        message = DataType("X", bytes=message_bytes).decode
        if not self.messages:
            self.messages.append(message)
            return node.fall_down
        original_message = self.messages[0]
        updated_message = f"{original_message} {message}"
        self.messages = [updated_message]
        return node.fall_down

    def error_check(self, node: KeyValue) -> str:
        if self.is_error(node.label):
            field_name = node.get_value("FIELD")
            reg = Register(node.get_value("BASE"))
            address = self.regs.get_unsigned_value(reg) + self.seg.evaluate(field_name)
            byte_array = DataType("X", input=node.get_value("XVALUE")).to_bytes()
            self.vm.set_bytes(byte_array, address, len(byte_array))
        return node.fall_down


class ExecutableMacro(RealTimeMacro, UserDefinedMacro):
    pass
