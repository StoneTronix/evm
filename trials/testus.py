from assembly import assembly
from interpreter import interpret


def test_assembly():
    assembly("./trials/test_program.asm", "./trials/test_program.bin")
    assert True

def test_interpret():
    interpret("./trials/test_program.bin", "./trials/test_result.yml", (0, 5))
    assert [1, 0, 1, 1, 0, 0]


