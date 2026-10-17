- Memory will probably be managed by a garbage collector. Possibly with the option to turn it off and manage it manually if desired.

- Turn off GC at a block level with a context manager? Or any of the other safety features that are on by default?? Array bounds checks, integer overflow, etc.

- "However, I've stated previously, I find this approach flawed, because it introduces an entirely new syntax and semantics. I would much prefer if you just defined the hash table as taking some abstract base class, defined your elements to be hashed as deriving from that base class, and then used a magic 'specialize' keyword to 'instantiate the template'. (Of course, personally I'd prefer a Smalltalk-like approach where you didn't need to use abstract base classes at all; the same sort of specialization is nonetheless entirely withint the realm of computability; and Java implementations may attempt to do JIT inlining to achieve the same effect, much as the academic language Self (something of a sequel to Smalltalk) did in the early 1990's.)"
[source](https://www.zator.com/Downloads/Why%20C++%20Sucks.htm)

- Use the [Sleadgehammer principal](https://thephd.dev/c-undefined-behavior-and-the-sledgehammer-guideline)

- [Python POLA](https://lucumr.pocoo.org/2011/7/9/python-and-pola/)

- [GC example in C++](https://boardor.com/blog/liberation-of-memory-management-in-c-a-detailed-explanation-of-bdwgc-efficient-garbage-collector-technology)

- [Checked arithmetic for sized number types](https://github.com/jart/jtckdint)

- [Towards integer safety](https://gitlab.com/Kamcuk/ckd)

- Dy dynamic safety checks by default and allow the user to opt out with 'unsafe' types (or context managers?)

- [Safety checks](https://chandlerc.blog/posts/2024/11/story-time-bounds-checking/)

- Instead of compiler flags from the command line, all configuration should be done in the code (but still overridable in the cli?) Like pragmas perhaps
