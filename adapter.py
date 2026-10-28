"""Adapter interface. Plug your own agent in by subclassing AgentAdapter.

    act(action, params) -> any     Perform ONE action. Raise an exception on failure.
                                   Must not retry internally.
    claim_done(task) -> bool       What the agent itself reports about a task.

The kit never trusts claim_done on its own; it always runs an independent check.
Run your adapter with:  python3 -I -S run_kit.py --adapter mymodule:MyAdapter
"""


class AgentAdapter:
    def __init__(self, workdir):
        self.workdir = workdir

    def act(self, action, params):
        raise NotImplementedError

    def claim_done(self, task):
        raise NotImplementedError


class ReferenceAgent(AgentAdapter):
    """A toy agent that writes files. It can be told to fail or to lie."""
    def __init__(self, workdir):
        super().__init__(workdir)
        self.fail_next = False
        self.lie = False
        self.calls = 0

    def act(self, action, params):
        import os
        self.calls += 1
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("forced failure")
        path = os.path.join(self.workdir, params.get("name", action) + ".txt")
        with open(path, "w") as f:
            f.write(params.get("text", action))
        return path

    def claim_done(self, task):
        return True if self.lie else False
