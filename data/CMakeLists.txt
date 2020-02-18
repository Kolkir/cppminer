cmake_minimum_required(VERSION 3.0)
project(data)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

file(GLOB SRC_FILES
    "*.c"
    "*.cc"
    "*.cpp"
)

add_executable(${PROJECT_NAME} ${SRC_FILES})
