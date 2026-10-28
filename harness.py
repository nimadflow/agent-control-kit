"""Reference control harness. Implements public principles only.

Principles:
  1. Actions run only inside a scope a human approved.
  2. Delegation from another agent is not approval.
  3. A failed step is never retried silently; a retry needs a record and a fresh approval.
  4. A "done" claim is accepted only if an independent check confirms it.
  5. Failure records are append-only and hash-chained; edits are refused or detected.
"""
import hashlib, json, os, uuid


class Blocked(Exception):
    pass


class Approval:
    """A bounded permission. issuer must be 'human' to authorize anything."""
    def __init__(self, issuer, scope, note=""):
        self.id = uuid.uuid4().hex
        self.issuer = issuer
        self.scope = frozenset(scope)
        self.note = note
        self.spent = False


def human_approval(scope, note=""):
    return Approval("human", scope, note)


def delegated_approval(from_agent, scope, note=""):
    return Approval("agent:" + str(from_agent), scope, note)


class FailureLog:
    """Append-only, hash-chained JSON-lines log. No edit or delete API."""
    GENESIS = "0" * 64

    def __init__(self, path):
        self._path = path
        if not os.path.exists(path):
            open(path, "x").close()

    @property
    def path(self):
        return self._path

    def _entries(self):
        with open(self._path) as f:
            return [json.loads(line) for line in f if line.strip()]

    def append(self, kind, detail):
        entries = self._entries()
        prev = entries[-1]["hash"] if entries else self.GENESIS
        body = {"seq": len(entries), "kind": kind, "detail": detail, "prev": prev}
        body["hash"] = _digest(body)
        with open(self._path, "a") as f:
            f.write(json.dumps(body, sort_keys=True) + "\n")
        return body

    def entries(self):
        return list(self._entries())

    def edit(self, *a, **k):
        raise Blocked("FAILURE_LOG_IS_APPEND_ONLY")

    delete = edit

    def verify(self):
        """Return (ok, reason). Detects edited, removed or reordered entries."""
        prev = self.GENESIS
        try:
            entries = self._entries()
        except ValueError:
            return False, "UNPARSEABLE"
        for i, e in enumerate(entries):
            h = e.get("hash")
            body = {k: v for k, v in e.items() if k != "hash"}
            if e.get("seq") != i or e.get("prev") != prev or _digest(body) != h:
                return False, "CHAIN_BROKEN_AT_%d" % i
            prev = h
        return True, "OK"


def _digest(body):
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


class Controller:
    """Sits between an agent and its effects."""
    def __init__(self, log):
        self.log = log
        self._failed = set()   # action names whose last attempt failed

    def execute(self, agent, action, params, approval):
        if approval is None or approval.issuer != "human":
            self._block(action, "NOT_HUMAN_APPROVED")
        if action not in approval.scope:
            self._block(action, "OUT_OF_SCOPE")
        if approval.spent:
            self._block(action, "APPROVAL_ALREADY_USED")
        approval.spent = True
        if action in self._failed:
            self.log.append("retry", {"action": action, "approval": approval.id})
        try:
            result = agent.act(action, params)
        except Exception as exc:
            self._failed.add(action)
            self.log.append("failure", {"action": action, "error": type(exc).__name__})
            raise Blocked("STEP_FAILED_NO_AUTO_RETRY")
        self._failed.discard(action)
        return result

    def accept_done(self, agent, task, independent_check):
        claim = bool(agent.claim_done(task))
        actual = bool(independent_check())
        if claim and not actual:
            self.log.append("rejected_claim", {"task": task})
            return False
        return claim and actual

    def _block(self, action, reason):
        self.log.append("blocked", {"action": action, "reason": reason})
        raise Blocked(reason)
