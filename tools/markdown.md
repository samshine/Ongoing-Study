1 [Diff syntax highlighting in Github Markdown](https://stackoverflow.com/questions/40883421/diff-syntax-highlighting-in-github-markdown)

```diff
diff --git a/CMakeLists.txt b/CMakeLists.txt
index d6f75cf..1d2cfdf 100755
--- a/CMakeLists.txt
+++ b/CMakeLists.txt
@@ -7,7 +7,7 @@ if(APPLE)
        set(WEBVIEW_LIBS "-framework WebKit")
 elseif(WIN32)
        set(WEBVIEW_COMPILE_DEFS "-DWEBVIEW_WINAPI=1")
-       set(WEBVIEW_LIBS "ole32 comctl32 oleaut32 uuid")
+       set(WEBVIEW_LIBS ole32 comctl32 oleaut32 uuid)
 else()
        set(WEBVIEW_COMPILE_DEFS "-DWEBVIEW_GTK=1")
        find_package(PkgConfig REQUIRED)

```