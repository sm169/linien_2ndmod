from pathlib import Path

from .bit2bin import bit2bin
from .hw_platform import Platform
from .linien_module import RootModule

REPO_ROOT_DIR = Path(__file__).resolve().parents[1]


def py_csrconstants(map, fil):
    fil.write("csr_constants = {\n")
    for k, v in root.linien.csrbanks.constants:
        fil.write("    '{}_{}': {},\n".format(k, v.name, v.value.value))
    fil.write("}\n\n")


def get_csrmap(banks):
    for name, csrs, map_addr, rmap in banks:
        reg_addr = 0
        for csr in csrs:
            yield [
                name,
                csr.name,
                map_addr,
                reg_addr,
                csr.size,
                not hasattr(csr, "status"),
            ]
            reg_addr += (csr.size + 8 - 1) // 8


def py_csrmap(it, fil):
    fil.write("csr = {\n")
    for reg in it:
        fil.write("    '{}_{}': ({}, 0x{:03x}, {}, {}),\n".format(*reg))
    fil.write("}\n")


if __name__ == "__main__":
    build_dir = REPO_ROOT_DIR / "gateware" / "build"
    bit2bin(
        build_dir / "top.bit",
        REPO_ROOT_DIR / "linien-server" / "linien_server" / "gateware.bin",
        flip=True,
    )
