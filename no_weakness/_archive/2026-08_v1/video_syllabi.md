# The video syllabi — transcribed

These are transcriptions of four phone screenshots that lived in `no_weakness/assets/` until August 2026. Each was a crop of a YouTube video's chapter-timestamp list. The images have been deleted; this file is what they contained.

They were referred to as "the syllabus" but they are not one. There is no hierarchy, no learning objective, no prerequisite, no indication of depth — only an ordinal number and a timestamp. Their sole remaining use is the coverage appendix in [`SYLLABUS.md`](../../SYLLABUS.md), which argues explicitly about which of these topics this repo covers and which it deliberately skips.

Two videos are represented. Neither covers SQL, MongoDB, TypeScript, or BigQuery.

---

## Video A — Python, 50 topics in ~51 minutes

Averages **61 seconds per topic**. That pace produces recognition, not retrieval, and it is precisely the depth level this folder exists to escape. Topic 50, `asyncio`, gets fifty-one seconds; the module covering the same ground in this repo runs several thousand words.

```
0:00   Intro
0:53    1. Arrays
1:54    2. Garbage collection with circular references
2:28    3. Not returning dicts & lists
3:27    4. Method Resolution Order
4:17    5. Walrus operator
5:07    6. operator.attrgetter
6:16    7. CPython
8:34    8. Global Interpreter Lock (GIL)
9:40    9. Concurrency
10:50  10. Multithreading
12:35  11. Multiprocessing
13:49  12. Multiprocessing race conditions
14:52  13. Shared memory in multiprocessing
15:24  14. collections
16:57  15. Encapsulation
18:21  16 & 17. Abstraction & abc
19:32  18. Inheritance
20:34  19. Polymorphism
21:21  20. Data model
22:24  21. Iterators
22:45  22. Generators
24:14  23. staticmethod & classmethod
25:14  24. Dependency injection
26:38  25. Parameterized testing
26:59  26. Fixtures for testing setup and teardown
27:50  27. Serialization & deserialization
28:39  28. getstate & setstate
29:29  29. heapq
31:25  30. Higher-order functions
32:18  31. filter
32:59  32. Advanced list comprehension
33:35  33. bytes
34:36  34. Bytecode and dis module
35:30  35. memoryview
36:37  36. metaclasses
37:58  37. Nesting & combining context managers
38:45  38. Custom context managers
39:26  39. weakref
40:00  40. del
40:06  41. WeakKeyDictionary & WeakValueDictionary
41:17  42. Optimizing memory with slots
42:14  43. memory_profiler
42:59  44. sys.getsizeof()
43:33  45. Advanced decorators
45:06  46. Dataclasses
46:49  47. Metaprogramming
47:18  48. functools
49:00  49. Advanced dataclass features
50:08  50. asyncio
```

## Video B — JavaScript, 14 sections in ~4.5 hours

The opposite depth profile: **roughly 19 minutes per section**, with Closure alone running a full hour. This is genuine teaching depth, and the section list is a reasonable skeleton for `04_javascript/`. The screenshot appears cut off at the bottom, so there may be further sections after "How Node.js works."

Note that it contains **zero TypeScript**.

```
0:00:00  Intro
0:01:45  Scope
0:11:02  Closure
1:11:08  Hoisting
1:16:52  Execution Context
2:03:48  Prototype
2:31:26  OOP
2:49:42  Event Propagation
2:59:37  Event Delegation
3:08:51  Asynchronous JavaScript
3:16:16  Memoization
3:34:22  Multi-threading in Browser
3:58:17  Multi-threading in Node.js
4:22:43  How Node.js works
```

---

## Provenance

Four unique images totalling roughly 725 KB, plus one exact duplicate. `python0_duplicate.jpeg` and `python_syllabus_1.jpeg` were byte-identical, both with sha1 `ba6c5f01b9502b782f00c46e47229e7b0b8814c6`. All five were deleted after this transcription was verified against them.
