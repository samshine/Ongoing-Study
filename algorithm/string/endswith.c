#include "endswith.h"

#include <string.h>

#ifdef __linux__
# include <strings.h>
#endif


bool endswith(const _TCHAR *s, const _TCHAR *s2)
{
    return endswithex(s, s2, _tcslen(s2));
}


bool endswithi(const _TCHAR *s, const _TCHAR *s2)
{
    return endswithiex(s, s2, _tcslen(s2));
}


bool endswithex(const _TCHAR *s, const _TCHAR *s2, size_t count)
{
    size_t slen = _tcslen(s);

    assert(count <= _tcslen(s2));

    if (slen < count)
        return false;

    return _tcsncmp(s + (slen - count), s2, count) == 0;
}


bool endswithiex(const _TCHAR *s, const _TCHAR *s2, size_t count)
{
    size_t slen = _tcslen(s);

    assert(count <= _tcslen(s2));

    if (slen < count)
        return false;

    return _tcsnicmp(s + (slen - count), s2, count) == 0;
}


// References:
// Ongoing-Study/c/Win32/Utils.c
// Ongoing-Study/cpp/strutils.hpp
// TortoiseGit/src/Utils/StringUtils.cpp
