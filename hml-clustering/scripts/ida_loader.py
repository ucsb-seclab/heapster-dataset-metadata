import sys
import os
import idaapi
import ida_idp
import idc
import ida_name
import idautils
import ida_auto
from idc_bc695 import MakeCode, MakeFunction, MakeDword, Dword, OpOffEx, SetFunctionCmt, Word



# You need to install this load in IDA to 
# properly load the blob and extract the information we need.

RAM_START = 0x20000000
RAM_SIZE  = 0x10000000

sys.stdout = open('/tmp/idalog', 'a')


def parse_blob_funcs(blob_funcs):
    global BASE_ADDR
    global FUNCTIONS

    data   = open(blob_funcs, "r")
    # First DWORD is the base address.
    BASE_ADDR = int(data.readline(), 16)
    if BASE_ADDR & 1:
        BASE_ADDR = BASE_ADDR + 1

    # The rest are functions
    FUNCTIONS = [int(p, 16) - 0x1 for p in data]

def accept_file(fd, fname):
    global TARGET
    global FNAME
    FNAME      = fname
    TARGET     = os.path.basename(fname)
    targetdir  = os.path.dirname(fname)
    blob_funcs = os.path.join(targetdir, 'hb_analysis', 'blob.funcs')
    if os.path.isfile(blob_funcs):
        parse_blob_funcs(blob_funcs)
        ret = {"format" : "Heapster (ARM)", "processor" : "arm"}
        return ret

# From: https://github.com/duo-labs/idapython/blob/master/cortex_m_firmware.py
def annotate_vector_table(vtoffset=0x0000000000):
        '''
        Name the vector table entries according to docs:
        http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0552a/BABIFJFG.html

        Vector tables can appear in mulitple places in device flash
        Functions are not renamed because multiple vectors might point to a single function
        Append the address of the VT entry to the name from self.annotations to keep unique names

        '''

        annotations = [
            "arm_initial_sp",
            "arm_reset",
            "arm_nmi",
            "arm_hard_fault",
            "arm_mm_fault",
            "arm_bus_fault",
            "arm_usage_fault",
            "arm_reserved1", "arm_reserved2", "arm_reserved3", "arm_reserved4",
            "arm_svcall",
            "arm_reserved_debug", "arm_reserved",
            "arm_pendsv",
            "arm_systick",
            "arm_irq_0", "arm_irq_1", "arm_irq_2", "arm_irq_3",
            "arm_irq_4", "arm_irq_5", "arm_irq_6", "arm_irq_7",
            "arm_irq_8", "arm_irq_9", "arm_irq_10", "arm_irq_11",
            "arm_irq_12", "arm_irq_13", "arm_irq_14", "arm_irq_15",
            "arm_irq_16", "arm_irq_17", "arm_irq_18", "arm_irq_19",
            "arm_irq_20", "arm_irq_21", "arm_irq_22", "arm_irq_23",
            "arm_irq_24", "arm_irq_25", "arm_irq_26", "arm_irq_27",
            "arm_irq_28", "arm_irq_29", "arm_irq_30", "arm_irq_31",
        ]

        for annotation_index, annotation in enumerate(annotations):
            entry_addr = vtoffset + 4 * annotation_index + BASE_ADDR
            entry_name = 'v_%s' % annotation
            func_addr  = Dword(entry_addr)
            func_name  = 'f_%s' % annotation

            #print('%s %s %s' % (entry_name, hex(entry_addr), func_addr))

            # Define the entry
            MakeDword(entry_addr)
            ida_name.set_name(entry_addr, entry_name, 0)

            # Define the function
            if func_addr != 0:
                func_addr = func_addr - 1
                define_function(func_addr, name=func_name)
                OpOffEx(entry_addr, 0, idaapi.REF_OFF32, -1, 0, 0)

                # Mark infinite loop functions
                instruction = Word(func_addr)
                if instruction == 0xe7fe:
                    SetFunctionCmt(func_addr, 'Infinite Loop', 1)

def define_function(addr, name=None):
    MakeCode(addr)
    MakeFunction(addr, idaapi.BADADDR)
    if name:
        ida_name.set_name(addr, name, 0)

def load_heapster_functions():
    for addr in FUNCTIONS:
        define_function(addr)

def get_file_size(fd):
    fd.seek(0, idaapi.SEEK_END)
    size = fd.tell()
    fd.seek(0)
    return size

def load_file(fd, neflags, format):
    global BASE_ADDR

    idaapi.set_processor_type("ARM:ARMv7-M", ida_idp.SETPROC_LOADER_NON_FATAL)
    size = get_file_size(fd)

    # Load the firmware
    fd.file2base(0, BASE_ADDR, BASE_ADDR + size, True)
    idaapi.add_segm(0, BASE_ADDR, BASE_ADDR + size, "ROM", "CODE")

    # Create RAM SECTION
    idaapi.add_segm(0, RAM_START, RAM_START + RAM_SIZE , "RAM", "DATA")

    annotate_vector_table()
    load_heapster_functions()

    ida_auto.auto_wait()
    print("[%s] Total functions found: %s" % (TARGET, len(list(idautils.Functions()))))
    # Bye
    sys.stdout.flush()
    x = idc.save_database(FNAME + '.idb')
    idc.qexit(0)
    return 1
