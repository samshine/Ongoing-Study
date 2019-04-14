#ifndef FOO_H_
#define FOO_H_

#ifdef __cplusplus
extern "C"
{
#endif

#if defined _WIN32 || defined __CYGWIN__
#  ifdef FOO_STATIC_LIB
#    define FOO_API
#  elif defined FOO_SHARED_LIB
#    if defined FOO_EXPORTS
#      if defined __GNUC__
#        define FOO_API __attribute__ ((dllexport))
#      elif defined _MSC_VER
#        define FOO_API __declspec(dllexport)
#      else
#        error Not tested yet!
#      endif
#    else
#      if defined __GNUC__
#        define FOO_API __attribute__ ((dllimport))
#      elif defined _MSC_VER
#        define FOO_API __declspec(dllimport)
#      else
#        error Not tested yet!
#      endif
#    endif
#  endif
#else
#  if defined __GNUC__ && __GNUC__ >= 4
#    define FOO_API __attribute__ ((visibility ("default")))
#  else
#    define FOO_API
#  endif
#endif


FOO_API int foo();
FOO_API const char *bar();

#ifdef __cplusplus
}
#endif

#endif


// References:
// https://gcc.gnu.org/wiki/Visibility
