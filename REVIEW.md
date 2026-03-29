# Project Review vs `spec.md`

1. [PASS] **AC #1: CLI startup + welcome + login/register prompt is implemented.**  
   - Spec reference: `spec.md:8-11`  
   - Code evidence: welcome/description printed in `main.py:83-84`; auth menu with create/login/exit in `main.py:20-23`.

2. [PASS] **AC #2 (registration): username/password collection and hashed password storage are implemented.**  
   - Spec reference: `spec.md:13-18`  
   - Code evidence: username/password prompts in `main.py:26-27`; `AuthManager.register_user` validates input in `auth.py:17-21`, stores hash via `hash_password` in `auth.py:27`; PBKDF2 hashing in `utils.py:59-63`.

3. [PASS] **AC #2 (registration success message and return-to-login flow) is implemented.**  
   - Spec reference: `spec.md:17-18`  
   - Code evidence: success text in `auth.py:29`; app prints message then loops back to auth menu (`main.py:29-30`, `main.py:19-23`).

4. [PASS] **AC #2 (login): credential validation against stored data is implemented.**  
   - Spec reference: `spec.md:19-22`  
   - Code evidence: login prompts in `main.py:33-35`; user lookup and password verification in `auth.py:35-39` using constant-time comparison in `utils.py:73`.

5. [PASS] **AC #3: post-login prompts for category, question count (5/10/15), and difficulty (easy/medium/hard/random) are implemented in correct order.**  
   - Spec reference: `spec.md:25-29`  
   - Code evidence: category selection in `main.py:44-58`, question count options in `main.py:61-68`, difficulty options in `main.py:71-79`, order in `main.py:94-100`.

6. [PASS] **AC #7: questions load from JSON and are filtered by difficulty.**  
   - Spec reference: `spec.md:31`  
   - Code evidence: JSON loading in `quiz.py:31-45`; difficulty filtering in `quiz.py:77-78`.

7. [PASS] **AC #9: liked/disliked feedback affects future question weighting.**  
   - Spec reference: `spec.md:32-34`  
   - Code evidence: feedback score logic in `quiz.py:62-67`; weighted sampling using those weights in `quiz.py:92-97` and `utils.py:116-141`.

8. [PASS] **AC #10: random selection is used when user has no feedback history.**  
   - Spec reference: `spec.md:35`  
   - Code evidence: fallback to `random.sample` in `quiz.py:89-90`.

9. [PASS] **AC #11: per-question display, type-specific input handling, immediate correctness feedback, correct answer-on-wrong, feedback prompt, and enter-to-continue are implemented.**  
   - Spec reference: `spec.md:38-49`  
   - Code evidence: question/choices display in `quiz.py:210-218`; typed input handling in `quiz.py:133-151`; immediate result in `quiz.py:223-228`; feedback prompt in `quiz.py:161-169`; enter-to-continue in `quiz.py:231`.

10. [PASS] **AC #13: question feedback is captured and persisted; default score exists for unseen questions.**  
    - Spec reference: `spec.md:53-58`  
    - Code evidence: feedback capture/storage in `quiz.py:155-171`; default score when no feedback in `quiz.py:63-64`.

11. [PASS] **AC #14: end-of-quiz score, percentage, and optional category stats are implemented.**  
    - Spec reference: `spec.md:61-65`  
    - Code evidence: total/percentage output in `quiz.py:235-236`; stats opt-in prompt in `quiz.py:240-247`; category average calculation in `utils.py:101-113` and display in `quiz.py:188-198`.

12. [WARN] **AC #15 is only partially met: data is obfuscated/non-human-readable, but cryptographic security is weak.**  
    - Spec reference: `spec.md:69-70`  
    - Code evidence: files are encoded/XOR-transformed in `utils.py:27-30` and `utils.py:44-56`, which makes content non-plain-text; however, encryption key is hardcoded (`utils.py:11`) and algorithm is reversible XOR (`utils.py:19-24`), so this should not be considered secure encryption.

13. [PASS] **AC #16: user can take another quiz or exit; subsequent quizzes reuse saved feedback data.**  
    - Spec reference: `spec.md:72-75`  
    - Code evidence: post-quiz loop in `main.py:93-107`; feedback persisted to `feedback.dat` in `quiz.py:171` and loaded for selection in `quiz.py:86-87`.

14. [PASS] **Error handling requirement: missing JSON file message is implemented exactly.**  
    - Spec reference: `spec.md:93-94`  
    - Code evidence: `"No JSON files to pull questions"` in `quiz.py:33` and `quiz.py:39`.

15. [PASS] **Error handling requirement: invalid input handling for menus and question types is implemented.**  
    - Spec reference: `spec.md:95-96`  
    - Code evidence: generic menu validation in `main.py:8-13`; question-type-specific validation in `quiz.py:133-153`; feedback/stats yes-no validation in `quiz.py:161-169` and `quiz.py:240-247`.

16. [PASS] **Error handling requirement: no category stats history message is implemented.**  
    - Spec reference: `spec.md:97-98`  
    - Code evidence: message `"Take more quizes in this category for stats"` in `quiz.py:195`.

17. [WARN] **Potential logic bug: category stats lookup is case-sensitive and exact-match only.**  
    - Impact: user may have history for `"Python Basics"` but entering `"python basics"` incorrectly reports no stats.  
    - Code evidence: raw input check `if category not in averages` in `quiz.py:193-195`.

18. [WARN] **Data integrity risk: corrupted encoded data silently resets to defaults.**  
    - Impact: `users.dat`, `scores.dat`, or `feedback.dat` can be overwritten and prior data lost without warning.  
    - Code evidence: when decode returns default and file is non-empty, file is overwritten in `utils.py:54-55`.

19. [WARN] **Missing file I/O exception handling on secure storage read/write paths.**  
    - Impact: permission/disk errors can crash the app instead of showing actionable messages.  
    - Code evidence: unguarded `write_text` in `utils.py:45`, `read_text` in `utils.py:52`, and JSON parse/decode pipeline in `utils.py:33-41` only handles decode exceptions, not read/write failures.

20. [WARN] **Security concern: no rate limiting or lockout on repeated failed logins.**  
    - Impact: vulnerable to local brute-force attempts against usernames.  
    - Code evidence: auth loop allows unlimited retries in `main.py:19-39`; no throttling logic in `auth.py`.

21. [WARN] **Code quality issue: some user-facing text is hard-coded and slightly misleading/repetitive.**  
    - Impact: maintenance/usability friction (e.g., fixed `A, B, C, D` text even if option count differs).  
    - Code evidence: message in `quiz.py:137`; repeated literal prompts/messages across `main.py` and `quiz.py`.

22. [PASS] **Hints feature from behavior description is implemented.**  
    - Spec reference: `spec.md:5` (hints mentioned in behavior description)  
    - Code evidence: `hint` command handling in `quiz.py:128-131` and hint generation in `utils.py:87-98`.

23. [WARN] **Spec/documentation mismatch: repository contains `spec.md` but spec file structure lists `SPEC.md`.**  
    - Impact: tooling or contributors expecting `SPEC.md` may fail to find it.  
    - Evidence: actual file is `spec.md` in workspace; listed as `SPEC.md` in `spec.md:89`.

24. [PASS] **Basic code health check: all Python modules compile successfully.**  
    - Evidence: `python3 -m py_compile main.py auth.py quiz.py utils.py` completed with no syntax errors.
