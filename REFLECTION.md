1. 
The raw build seemed to have core features that were specified, such as choosing question types, and receiving and implementing feedback- I would say it met around 90% of my acceptance criteria. 
2. 
There was no intervention needed. I just used Copilot to generate more questions for each category and difficulty level to have a minimum number of questions to generate stats. I should have specified what to do if there weren’t enough questions in a certain category selected.
3. 
The review flagged some of the file names- for example, “spec.md” as opposed to “SPEC.md”, which I am not sure was an actual problem. 
There were some security issues that were flagged, such as “Data integrity risk: corrupted encoded data silently resets to defaults” and repeated or hardcoded implementation of security features, and no rate limiting or lockout on repeated failed logins. These are things I could have been more specific about in my SPEC.md.
4. 
I think I could have been more specific about the interface. The introduction to the app is important- I could have been more specific about what I wanted in each page of the entry, and exactly the types of inputs I wanted handled based on the user type (new versus experienced user.)
5. 
I would use this workflow for all my future projects, because it is way more efficient than conversational back-and-forth, especially if I already have a specific vision for the app.  Plan-delegate-review would be worse if one is in the initial brainstorming phase of their development. Writing a SPEC.md allowed me to develop a framework for the app and think through specific parts of the app. Starting with conversational back-and-forth often leads to planning on the fly, and often after the AI has generated the code.