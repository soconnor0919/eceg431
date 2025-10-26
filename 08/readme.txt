Project 8: Stack Flow Control (VM II)

The description for this project is found at:

https://www.nand2tetris.org/project08

You may _absolutely_ work as pairs on this project.

Hints:

a) Use the proposed API in chapter 8 that splits the tasks across "modules."

b) You will need to build upon and re-use your VMTranslator from project 7. If you didn't get it done, well, you'll need to for this project!

b) Test using the proposed order in chapter 8. The programs test increasingly more functionality as they go.

Perspective:

What you're building is essentially how _all_ function calls work in modern computing. Computers have an ABI (application binary interface) and these tend to be related to the C calling convention. What that means is that for a particular system (OS and platform/architecture), all programming languages use a mutually-agreed upon interface (the ABI), which when used means that a function written in and compiled frmo language A can call a function written in compiled from language B and all is well. This also means we can use standard libraries once we know the interface.

Most compilers (or even architectures) have their prescribed format that describes what information and the oder that it is placed on the stack. The x86 standard is similar to the VM translator you are currently writing. The way in which an OS kernel handles tasks is also similar, except that it allows multiple processes to run and switches between these. To do this, it provides each process or thread its own stack. Guess what? To switch processes, you just store everything on the current stack, set the stack pointer to the other processes' stack, pop it off, and keep going. The OS kernel is responsible for switching between the various tasks/threads and giving each process its time on the system.

For further reading, search for terms like "calling convention" or "ABI" which stands for Application Binary Interface. There are a few different ones out there, like ABI for x86_64 on linux, or the Micorosoft ABI, and they are how stack frames are saved on the stack and functions are called. Once you know the ABI, you can then call functions compiled in other languages. There's a lot of power this opens up.

Remember that the gradescope tester is including a "-y" and a "-n" flag at the end of the command. This indicates whether or not your compiler should include the bootstrap code (-y) or not (-n).
