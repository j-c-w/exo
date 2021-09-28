from .prelude import *
from .LoopIR import LoopIR, LoopIR_Rewrite, Alpha_Rename, LoopIR_Do, PAST
from . import pyparser
from .LoopIR import T
import re

from collections import ChainMap
import inspect

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# Parse Fragment Errors

class ParseFragmentError(Exception):
    pass


# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# General Fragment Parsing

def parse_fragment(proc, pattern_str, stmt, call_depth=0):
    # get source location where this is getting called from
    caller = inspect.getframeinfo(inspect.stack()[call_depth+1][0])

    # parse the pattern we're going to use to match
    p_ast         = pyparser.pattern(pattern_str,
                                     filename=caller.filename,
                                     lineno=caller.lineno)
    assert len(p_ast) == 1

    return ParseFragment(p_ast[0], proc, stmt).results()


_PAST_to_LoopIR = {
  # list of exprs
  list:               list,
  #
  PAST.Read:          LoopIR.Read,
  PAST.Const:         LoopIR.Const,
  PAST.USub:          LoopIR.USub,
  PAST.BinOp:         LoopIR.BinOp,
  PAST.StrideExpr:    LoopIR.StrideExpr,
}


class BuildEnv(LoopIR_Do):
    def __init__(self, proc, stmt):
        self.env       = ChainMap()
        self.found_trg = False
        self.trg       = stmt
        self.proc      = proc

        for a in self.proc.args:
            self.env[a.name] = a.type
            self.do_t(a.type)
        for p in self.proc.preds:
            self.do_e(p)

        self.do_stmts(self.proc.body)

    def result(self):
        return self.env

    def push(self):
        self.env = self.env.new_child()

    def pop(self):
        self.env = self.env.parents

    def do_s(self, s):
        if self.found_trg:
            return

        styp = type(s)
        if styp is LoopIR.Assign or styp is LoopIR.Reduce:
            self.env[s.name] = s.type
            for e in s.idx:
                self.do_e(e)
            self.do_e(s.rhs)
            self.do_t(s.type)
        elif styp is LoopIR.ForAll or styp is LoopIR.Seq:
            self.env[s.iter] = T.index
            self.do_e(s.hi)
            self.do_stmts(s.body)
        elif styp is LoopIR.Alloc:
            self.env[s.name] = s.type
            self.do_t(s.type)

        super().do_s(s)

        if s is self.trg:
            self.found_trg = True


class ParseFragment:
    def __init__(self, pat, proc, stmt):
        self._results   = None # results should be expression

        assert isinstance(pat, PAST.expr)

        env = BuildEnv(proc, stmt).result()

        if type(pat) is PAST.Read:
            nm  = self.find_sym(pat, env)
            idx = [ self.find_sym(i) for i in pat.idx ]
            self._results = LoopIR.Read(nm, idx, env[nm], stmt.srcinfo)
        elif type(pat) is PAST.StrideExpr:
            nm = self.find_sym(pat.name, env)
            self._results = LoopIR.StrideExpr(nm, pat.dim, T.stride, stmt.srcinfo)

    def find_sym(self, expr, env):
        for k in env.keys():
            if expr == str(k):
                return k

    def results(self):
        return self._results

