"""Thompson construction: regex -> epsilon-NFA (Task 4.5).

Supports literals, escapes, [classes], groups, |, ?, *, +, {m}, {m,n}.
"""
import re


class Frag:
    def __init__(self, start, accept):
        self.start, self.accept = start, accept


class Thompson:
    def __init__(self, pattern):
        self.pattern, self.i, self.n = pattern, 0, 0
        self.trans = {}   # state -> list of (label, target); label None = epsilon, else frozenset of chars
        frag = self._alt()
        self.start, self.accept = frag.start, frag.accept

    def _new(self):
        self.n += 1
        self.trans[self.n] = []
        return self.n

    def _eps(self, a, b):
        self.trans[a].append((None, b))

    def _peek(self):
        return self.pattern[self.i] if self.i < len(self.pattern) else None

    def _alt(self):
        f = self._cat()
        while self._peek() == "|":
            self.i += 1
            g = self._cat()
            s, a = self._new(), self._new()
            for x in (f, g):
                self._eps(s, x.start); self._eps(x.accept, a)
            f = Frag(s, a)
        return f

    def _cat(self):
        frags = []
        while self._peek() not in (None, "|", ")"):
            frags.append(self._rep())
        if not frags:
            s = self._new(); return Frag(s, s)
        f = frags[0]
        for g in frags[1:]:
            self._eps(f.accept, g.start)
            f = Frag(f.start, g.accept)
        return f

    def _rep(self):
        start_i = self.i
        f = self._atom()
        atom_src = self.pattern[start_i:self.i]
        c = self._peek()
        if c in ("*", "+", "?"):
            self.i += 1
            s, a = self._new(), self._new()
            self._eps(s, f.start); self._eps(f.accept, a)
            if c in ("*", "?"): self._eps(s, a)          # bypass: optionality
            if c in ("*", "+"): self._eps(f.accept, f.start)
            return Frag(s, a)
        if c == "{":
            j = self.pattern.index("}", self.i)
            lo, _, hi = self.pattern[self.i + 1:j].partition(",")
            self.i = j + 1
            lo = int(lo); hi = lo if _ == "" else (int(hi) if hi else None)
            parts = []
            for _k in range(lo):
                parts.append(Thompson(atom_src)._as_frag(self))
            if hi is None:
                parts.append(self._star_of(atom_src))
            else:
                for _k in range(hi - lo):
                    o = Thompson(atom_src)._as_frag(self)
                    s, a = self._new(), self._new()
                    self._eps(s, o.start); self._eps(o.accept, a); self._eps(s, a)
                    parts.append(Frag(s, a))
            if not parts:
                s = self._new(); return Frag(s, s)
            g = parts[0]
            for h in parts[1:]:
                self._eps(g.accept, h.start); g = Frag(g.start, h.accept)
            return g
        return f

    def _star_of(self, src):
        o = Thompson(src)._as_frag(self)
        s, a = self._new(), self._new()
        self._eps(s, o.start); self._eps(o.accept, a); self._eps(s, a); self._eps(o.accept, o.start)
        return Frag(s, a)

    def _as_frag(self, host):
        """Copy this sub-NFA into `host` with fresh state numbers."""
        mapping = {}
        for s in self.trans:
            mapping[s] = host._new()
        for s, edges in self.trans.items():
            for lab, t in edges:
                host.trans[mapping[s]].append((lab, mapping[t]))
        return Frag(mapping[self.start], mapping[self.accept])

    def _atom(self):
        c = self._peek()
        if c == "(":
            self.i += 1
            if self.pattern.startswith("?:", self.i):
                self.i += 2
            f = self._alt()
            assert self._peek() == ")"
            self.i += 1
            return f
        if c == "[":
            j = self.pattern.index("]", self.i)
            body = self.pattern[self.i + 1:j]
            self.i = j + 1
            chars = set()
            k = 0
            while k < len(body):
                if k + 2 < len(body) and body[k + 1] == "-":
                    chars.update(chr(x) for x in range(ord(body[k]), ord(body[k + 2]) + 1)); k += 3
                else:
                    chars.add(body[k]); k += 1
            return self._sym(frozenset(chars))
        if c == "\\":
            self.i += 2
            return self._sym(frozenset(self.pattern[self.i - 1]))
        self.i += 1
        return self._sym(frozenset(c))

    def _sym(self, label):
        s, a = self._new(), self._new()
        self.trans[s].append((label, a))
        return Frag(s, a)

    # ----- simulation -----
    def _closure(self, S):
        out, st = set(S), list(S)
        while st:
            x = st.pop()
            for lab, t in self.trans[x]:
                if lab is None and t not in out:
                    out.add(t); st.append(t)
        return out

    def fullmatch(self, s):
        cur = self._closure({self.start})
        for ch in s:
            cur = self._closure({t for x in cur for lab, t in self.trans[x] if lab is not None and ch in lab})
            if not cur:
                return False
        return self.accept in cur

    def size(self):
        return len(self.trans), sum(len(v) for v in self.trans.values())
