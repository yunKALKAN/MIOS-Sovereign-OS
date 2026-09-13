import time
import hashlib
from dataclasses import dataclass

# =========================
# BLACKMASTER VM (SINGLE BLOCK CORE)
# =========================

class CFEL:
    def __init__(self):
        self.chain = []

    def commit(self, event: dict):
        event = dict(event)
        event["ts"] = time.time()
        event["hash"] = hashlib.sha256(str(sorted(event.items())).encode()).hexdigest()
        self.chain.append(event)
        return event

    def state(self):
        trust = 0.5
        for e in self.chain:
            if e.get("op") == "EXEC":
                trust += 0.02
            elif e.get("op") == "BLOCK":
                trust -= 0.03
        return max(0.0, min(1.0, trust))


@dataclass
class EU:
    content: str
    layer: str


class BlackMasterVM:

    def __init__(self):
        self.cfel = CFEL()
        self.version = 1

    def compile(self, text: str):
        t = text.lower()

        if "rule" in t or "governance" in t:
            return "GOV_BLOCK", "GOVERNANCE"

        if "must" in t or "should" in t:
            return "SPEC_CHECK", "SPECIFICATION"

        if "execute" in t or "run" in t:
            return "EXEC_RUN", "IMPLEMENTATION"

        return "NOOP", "MEANING"

    def gate(self, bytecode: str):
        return bytecode == "EXEC_RUN"

    def execute(self, bytecode: str):
        if bytecode == "EXEC_RUN":
            return "EXEC"
        if bytecode == "SPEC_CHECK":
            return "SPEC"
        if bytecode == "GOV_BLOCK":
            return "BLOCK"
        return "NOOP"

    def trust(self):
        return self.cfel.state()

    def run(self, text: str):

        bytecode, layer = self.compile(text)
        allowed = self.gate(bytecode)
        op = self.execute(bytecode)

        event = self.cfel.commit({
            "op": op,
            "bytecode": bytecode,
            "layer": layer,
            "content": text
        })

        if allowed:
            self.version += 1

        return {
            "status": "OK" if allowed else "BLOCKED",
            "bytecode": bytecode,
            "layer": layer,
            "trust": self.trust(),
            "version": self.version,
            "event": event
        }


if __name__ == "__main__":
    vm = BlackMasterVM()

    print(vm.run("this is a governance rule"))
    print(vm.run("must follow specification"))
    print(vm.run("execute smart contract tx 0xabc"))
    print(vm.run("run computation task"))
