// 2014-06-25T22:51+08:00
#include <iostream>

// 2017-11-19T17-34+08:00
// In a multi-line macro, you can not use single line comment with `//`.
// https://stackoverflow.com/questions/11721981/macros-and-multi-line-comments
#define SWAP_T(T, x, y) \
    do { \
        // This is a single line comment. \
        T tmp = x; \
        x = y; \
        y = tmp; \
    } while (0)


int main()
{
    // \
    std::cout << "Hello, world!" << std::endl;

    // while, you will see nothing on the screen. \
    Because the "\" at the end of the comment makes the "std::cout..." a \
    multi-line comment.

    return 0;
}

// References:
// [C++ Multi-line comments using backslash](http://stackoverflow.com/questions/7059549/c-multi-line-comments-using-backslash)
// [Backslash newline at end of file warning](http://stackoverflow.com/questions/5708259/backslash-newline-at-end-of-file-warning)
