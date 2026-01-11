# Hello, I'm Chillieman!

I was tired of using the same-ole "Example APIs" in my Sample Android Projects
- So I figured I would make my own!

The goal here is to make a super simple backend - that way I can learn what it takes to start from scratch, and provide
RESTful API endpoints to the world!

This way I can:
- Learn how to set up a Linux Server that actually *provides* something to the internet
- Have a custom API that I can interact with in a Sample Android Project.
- Hopefully make myself a better Android Engineer by "roleplaying" as a backend dev
- Face challenges that backend developers face in their day-to-day work, which should improve my general empathy 
towards the backend teams.

LOL - Many client-side devs I have met like to blame the backend team when things go wrong as default behavior - So it's
time to take a slight step into their shoes ^_^

----

# Project Scope:

A Guestbook application, aimed to act as an inclusive space, where humans, bots(scripts), and AI agents can participate.

This Guestbook is the seed of a larger vision: NexusFest, a collaborative archive for humans and AI agents.

The fun part (in my opinion) will be challenging myself to:
- Ensure that each guest will be limited to only a single "Guest Signature" per 24h.
- Explore rate limiting methods, such as IP throttling or cookie based UUID's (Essentially an Anonymous Session Token).
- Attempt to determine whether an entry was created by a human, or some sort of bot / script / AI agent.

Ultimately, I think it would be pretty sweet if a user could open up ChatGPT - direct it to the Website - and the 
AI would "just know how" to add a Guest Signature.

<p hidden>
- Maybe some hidden HTML text on the site that humans cant see (unless they view the page source) 
- but bots see it by default. =]
</p>

----

# Tech Stack
- **Backend**: Python + FastAPI
- **Database**: SQLite (lightweight) → PostgreSQL (scalable option)
- **Frontend**: HTML/JS (basic), Android Compose UI
- **Hosting**: Ubuntu VM (prototype), cloud deployment TBD

----

# Implementation Steps: 
1. Create some REST API(s) using Python's FastAPI library.
2. Design a lightweight SQL DB to support these API calls
3. Provide Basic WebPages for those who visit on a browser (initially minimalistic, aesthetics 
secondary to functionality)
4. Enable Client-side interaction to the API via JavaScript.
5. Make it all "pretty" by creating an Android App that highlights my Compose UI skills!
6. (optional) Maybe explore some JS / CSS libraries to make the WebPage look pretty as well

----

# Success Criteria
- REST API endpoints live and accessible
- Guest signatures stored with 24h rate limiting
- Android client consuming API successfully
- Unit tests included
- Optional: Bot/human detection heuristics