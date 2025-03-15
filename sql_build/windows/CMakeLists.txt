cmake_minimum_required(VERSION 3.10)
project(sqlite-dll LANGUAGES C)

# Настройка для DLL
add_library(sqlite SHARED
    sqlite-src/sqlite-amalgamation-3260000/sqlite3.c
    sqlite-src/sqlite-amalgamation-3260000/sqlite3.h
)

set_target_properties(sqlite PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS TRUE
    OUTPUT_NAME "sqlite3" # Убираем "lib" из названия
    PREFIX "" # Убираем префикс "lib"
)

# Установка библиотеки
install(TARGETS sqlite
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)