#include <locale.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

#include <tchar.h>
#define WIN32_LEAN_AND_MEAN
#include <Windows.h>

#include "../base64.h"
#include "dump.h"
#include "wconv.h"


void do_test(const _TCHAR *str)
{
    char u8str_buffer[256];
    char ansi_buffer[256];

#ifdef _UNICODE
    char *u8str = TCHAR_TO_UTF8(str);
    _putts(_T("------------------------------------------------------------"));

    if (u8str == NULL)
    {
        _ftprintf(stderr, _T("Failed to convert input string to utf-8 string!\n"));
        return;
    }

    char *astr = TCHAR_TO_ANSI(str);
#else
    const char *u8str = str;
    const char *astr = str;
#endif

    if (easy_base64_encode(u8str, strlen(u8str), u8str_buffer, sizeof(u8str_buffer)) != NULL &&
        easy_base64_encode(astr, strlen(astr), ansi_buffer, sizeof(ansi_buffer)))
    {
        _tprintf(_T("Original        : %s\n"), str);
        _tprintf(_T("Raw bytes(utf-8): "));
        dump_data(u8str, strlen(u8str));
        _tprintf(_T("Raw bytes(ansi) : "));
        dump_data(astr, strlen(astr));

        _tprintf(
#ifdef _UNICODE
            _T("Base64(utf-8)   : %S\n")
            _T("Base64(ansi)    : %S\n")
#else
            _T("Base64(utf-8)   : %s\n")
            _T("Base64(ansi)    : %s\n")
#endif
            ,
            u8str_buffer,
            ansi_buffer
        );
    }
    else
    {
        _ftprintf(stderr, _T("Failed to encode the input string!\n"));
    }

#ifdef _UNICODE
    free(u8str);
    free(astr);
#endif
}


int _tmain(int argc, _TCHAR *argv[])
{
#ifdef _UNICODE
    _tsetlocale(LC_ALL, _T(""));
#endif

    do_test(_T("Good morning."));
    do_test(_T("おはよう"));
    do_test(_T("早上好！"));

    return 0;
}


// References:
// https://stackoverflow.com/questions/10439680/wchar-t-and-encoding
// https://stackoverflow.com/questions/3996026/what-is-the-default-encoding-for-c-strings
// https://stackoverflow.com/questions/6794590/how-does-file-encoding-affect-c11-string-literals

/*
> wchar_tests.exe
------------------------------------------------------------
Original        : Good morning.
Raw bytes(utf-8): Good morning.
Raw bytes(ansi) : Good morning.
Base64(utf-8)   : R29vZCBtb3JuaW5nLg==
Base64(ansi)    : R29vZCBtb3JuaW5nLg==
------------------------------------------------------------
Original        : おはよう
Raw bytes(utf-8): \xe3\x81\x8a\xe3\x81\xaf\xe3\x82\x88\xe3\x81\x86
Raw bytes(ansi) : \xa4\xaa\xa4\xcf\xa4\xe8\xa4\xa6
Base64(utf-8)   : 44GK44Gv44KI44GG
Base64(ansi)    : pKqkz6TopKY=
------------------------------------------------------------
Original        : 早上好！
Raw bytes(utf-8): \xe6\x97\xa9\xe4\xb8\x8a\xe5\xa5\xbd\xef\xbc\x81
Raw bytes(ansi) : \xd4\xe7\xc9\xcf\xba\xc3\xa3\xa1
Base64(utf-8)   : 5pep5LiK5aW977yB
Base64(ansi)    : 1OfJz7rDo6E=

> char_tests.exe
Original        : Good morning.
Raw bytes(utf-8): Good morning.
Raw bytes(ansi) : Good morning.
Base64(utf-8)   : R29vZCBtb3JuaW5nLg==
Base64(ansi)    : R29vZCBtb3JuaW5nLg==
Original        : おはよう
Raw bytes(utf-8): \xa4\xaa\xa4\xcf\xa4\xe8\xa4\xa6
Raw bytes(ansi) : \xa4\xaa\xa4\xcf\xa4\xe8\xa4\xa6
Base64(utf-8)   : pKqkz6TopKY=
Base64(ansi)    : pKqkz6TopKY=
Original        : 早上好！
Raw bytes(utf-8): \xd4\xe7\xc9\xcf\xba\xc3\xa3\xa1
Raw bytes(ansi) : \xd4\xe7\xc9\xcf\xba\xc3\xa3\xa1
Base64(utf-8)   : 1OfJz7rDo6E=
Base64(ansi)    : 1OfJz7rDo6E=

> py
>>> from base64 import *
>>> b64encode('早上好！'.encode('utf-8'))
b'5pep5LiK5aW977yB'
>>> b = 
>>> b64encode('早上好！'.encode('gbk'))
b'1OfJz7rDo6E='
*/
