/**
 * RedSand Monitoring Agent - C++ агент для мониторинга системы
 * 
 * Компоненты:
 * - Перехват API вызовов через MinHook
 * - Мониторинг через ETW (Event Tracing for Windows)
 * - Отправка событий оркестратору через named pipes
 * 
 * Сборка на Windows:
 *   cl /LD agent.cpp /Fe:RedSandAgent.dll /link kernel32.lib advapi32.lib ws2_32.lib
 */

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tlhelp32.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "kernel32.lib")
#pragma comment(lib, "advapi32.lib")
#pragma comment(lib, "ws2_32.lib")

// Конфигурация
#define MAX_PATH_LENGTH 512
#define MAX_EVENTS_BUFFER 1024
#define PIPE_NAME "\\\\.\\pipe\\RedSandPipe"
#define LOG_FILE "logs/agent.log"

// Типы событий
typedef enum {
    EVENT_FILE_CREATE = 1,
    EVENT_FILE_DELETE,
    EVENT_FILE_WRITE,
    EVENT_REGISTRY_SET,
    EVENT_REGISTRY_DELETE,
    EVENT_PROCESS_CREATE,
    EVENT_PROCESS_TERMINATE,
    EVENT_NETWORK_CONNECT,
    EVENT_NETWORK_SEND,
    EVENT_DLL_LOAD,
    EVENT_INJECTION
} EventType;

// Структура события
typedef struct {
    DWORD timestamp;
    EventType type;
    DWORD pid;
    DWORD tid;
    char data[MAX_PATH_LENGTH];
    DWORD dataSize;
} EventRecord;

// Глобальные переменные
static HANDLE hPipe = INVALID_HANDLE_VALUE;
static FILE* logFile = NULL;
static BOOL isMonitoring = FALSE;

// Функции логирования
void LogMessage(const char* format, ...) {
    if (!logFile) {
        logFile = fopen(LOG_FILE, "a");
        if (!logFile) return;
    }
    
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    char timeBuffer[26];
    strftime(timeBuffer, 26, "%Y-%m-%d %H:%M:%S", tm_info);
    
    fprintf(logFile, "[%s] ", timeBuffer);
    
    va_list args;
    va_start(args, format);
    vfprintf(logFile, format, args);
    va_end(args);
    
    fprintf(logFile, "\n");
    fflush(logFile);
}

// Отправка события оркестратору
BOOL SendEvent(EventRecord* event) {
    if (hPipe == INVALID_HANDLE_VALUE) {
        // Попытка подключения к pipe
        hPipe = CreateFile(
            PIPE_NAME,
            GENERIC_WRITE,
            0,
            NULL,
            OPEN_EXISTING,
            0,
            NULL
        );
        
        if (hPipe == INVALID_HANDLE_VALUE) {
            LogMessage("Не удалось подключиться к pipe: %d", GetLastError());
            return FALSE;
        }
    }
    
    DWORD bytesWritten;
    BOOL result = WriteFile(hPipe, event, sizeof(EventRecord), &bytesWritten, NULL);
    
    if (!result) {
        LogMessage("Ошибка записи в pipe: %d", GetLastError());
        CloseHandle(hPipe);
        hPipe = INVALID_HANDLE_VALUE;
    }
    
    return result;
}

// Логирование события файла
void LogFileEvent(EventType type, const char* path, DWORD pid) {
    EventRecord event = {0};
    event.timestamp = GetTickCount();
    event.type = type;
    event.pid = pid;
    event.tid = GetCurrentThreadId();
    strncpy_s(event.data, path, MAX_PATH_LENGTH - 1);
    event.dataSize = strlen(path);
    
    SendEvent(&event);
    
    const char* typeStr = "";
    switch(type) {
        case EVENT_FILE_CREATE: typeStr = "CREATE"; break;
        case EVENT_FILE_DELETE: typeStr = "DELETE"; break;
        case EVENT_FILE_WRITE: typeStr = "WRITE"; break;
    }
    
    LogMessage("[FILE] %s: %s (PID: %d)", typeStr, path, pid);
}

// Логирование события реестра
void LogRegistryEvent(EventType type, const char* key, const char* value, DWORD pid) {
    EventRecord event = {0};
    event.timestamp = GetTickCount();
    event.type = type;
    event.pid = pid;
    event.tid = GetCurrentThreadId();
    
    char buffer[MAX_PATH_LENGTH];
    sprintf_s(buffer, "%s\\%s", key, value ? value : "");
    strncpy_s(event.data, buffer, MAX_PATH_LENGTH - 1);
    event.dataSize = strlen(buffer);
    
    SendEvent(&event);
    
    const char* typeStr = type == EVENT_REGISTRY_SET ? "SET" : "DELETE";
    LogMessage("[REGISTRY] %s: %s (PID: %d)", typeStr, buffer, pid);
}

// Логирование сетевого события
void LogNetworkEvent(const char* ip, int port, const char* domain, DWORD pid) {
    EventRecord event = {0};
    event.timestamp = GetTickCount();
    event.type = EVENT_NETWORK_CONNECT;
    event.pid = pid;
    event.tid = GetCurrentThreadId();
    
    char buffer[MAX_PATH_LENGTH];
    if (domain && strlen(domain) > 0) {
        sprintf_s(buffer, "%s:%d (%s)", ip, port, domain);
    } else {
        sprintf_s(buffer, "%s:%d", ip, port);
    }
    strncpy_s(event.data, buffer, MAX_PATH_LENGTH - 1);
    event.dataSize = strlen(buffer);
    
    SendEvent(&event);
    LogMessage("[NETWORK] Connect: %s (PID: %d)", buffer, pid);
}

// Логирование события процесса
void LogProcessEvent(EventType type, const char* processName, DWORD pid, DWORD ppid) {
    EventRecord event = {0};
    event.timestamp = GetTickCount();
    event.type = type;
    event.pid = pid;
    event.tid = GetCurrentThreadId();
    
    char buffer[MAX_PATH_LENGTH];
    sprintf_s(buffer, "%s (PPID: %d)", processName, ppid);
    strncpy_s(event.data, buffer, MAX_PATH_LENGTH - 1);
    event.dataSize = strlen(buffer);
    
    SendEvent(&event);
    
    const char* typeStr = type == EVENT_PROCESS_CREATE ? "CREATE" : "TERMINATE";
    LogMessage("[PROCESS] %s: %s (PID: %d)", typeStr, buffer, pid);
}

// Мониторинг процессов через Toolhelp32 Snapshot
DWORD MonitorProcesses() {
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE) {
        LogMessage("Ошибка создания snapshot процессов");
        return 1;
    }
    
    PROCESSENTRY32 pe32 = {0};
    pe32.dwSize = sizeof(PROCESSENTRY32);
    
    if (!Process32First(hSnapshot, &pe32)) {
        CloseHandle(hSnapshot);
        return 1;
    }
    
    do {
        LogProcessEvent(EVENT_PROCESS_CREATE, pe32.szExeFile, pe32.th32ProcessID, pe32.th32ParentProcessID);
    } while (Process32Next(hSnapshot, &pe32));
    
    CloseHandle(hSnapshot);
    return 0;
}

// Хуки для перехвата API (упрощенная версия без MinHook для демонстрации)
// В полной версии использовать MinHook для перехвата:
// - CreateFileA/W
// - DeleteFileA/W
// - RegSetValueExA/W
// - connect (Winsock)
// - CreateProcessA/W

// Пример перехвата CreateFile (требует MinHook)
/*
#include "MinHook.h"

typedef HANDLE (WINAPI *CreateFileA_t)(LPCSTR, DWORD, DWORD, LPSECURITY_ATTRIBUTES, DWORD, DWORD, HANDLE);
static CreateFileA_t TrueCreateFileA = NULL;

HANDLE WINAPI HookedCreateFileA(
    LPCSTR lpFileName,
    DWORD dwDesiredAccess,
    DWORD dwShareMode,
    LPSECURITY_ATTRIBUTES lpSecurityAttributes,
    DWORD dwCreationDisposition,
    DWORD dwFlagsAndAttributes,
    HANDLE hTemplateFile
) {
    HANDLE result = TrueCreateFileA(lpFileName, dwDesiredAccess, dwShareMode, 
                                     lpSecurityAttributes, dwCreationDisposition, 
                                     dwFlagsAndAttributes, hTemplateFile);
    
    if (result != INVALID_HANDLE_VALUE) {
        EventType type = EVENT_FILE_CREATE;
        if (dwCreationDisposition == OPEN_EXISTING) {
            type = EVENT_FILE_WRITE;
        }
        LogFileEvent(type, lpFileName, GetCurrentProcessId());
    }
    
    return result;
}
*/

// Инициализация агента
BOOL InitializeAgent() {
    LogMessage("Инициализация агента RedSand...");
    
    // Создание директории для логов
    CreateDirectoryA("logs", NULL);
    
    // Открытие файла логов
    logFile = fopen(LOG_FILE, "a");
    if (!logFile) {
        printf("Не удалось открыть файл логов\n");
        return FALSE;
    }
    
    // Подключение к pipe оркестратора
    hPipe = CreateFile(
        PIPE_NAME,
        GENERIC_WRITE,
        0,
        NULL,
        OPEN_EXISTING,
        0,
        NULL
    );
    
    if (hPipe != INVALID_HANDLE_VALUE) {
        LogMessage("Подключено к оркестратору через pipe");
    } else {
        LogMessage("Оркестратор не найден, работа в автономном режиме");
    }
    
    isMonitoring = TRUE;
    LogMessage("Агент запущен");
    
    return TRUE;
}

// Остановка агента
void StopAgent() {
    LogMessage("Остановка агента...");
    isMonitoring = FALSE;
    
    if (hPipe != INVALID_HANDLE_VALUE) {
        CloseHandle(hPipe);
        hPipe = INVALID_HANDLE_VALUE;
    }
    
    if (logFile) {
        fclose(logFile);
        logFile = NULL;
    }
}

// Точка входа для DLL
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            DisableThreadLibraryCalls(hModule);
            InitializeAgent();
            break;
        case DLL_PROCESS_DETACH:
            StopAgent();
            break;
    }
    return TRUE;
}

// Экспортируемая функция для запуска извне
__declspec(dllexport) void StartMonitoring() {
    InitializeAgent();
    
    // Начальный снимок процессов
    MonitorProcesses();
    
    LogMessage("Мониторинг активен. Нажмите Ctrl+C для остановки.");
    
    // Основной цикл мониторинга
    while (isMonitoring) {
        Sleep(1000);
        
        // Здесь должна быть логика периодического опроса
        // В полной версии: обработка ETW событий, проверка хуков
    }
    
    StopAgent();
}

// Консольное приложение для тестирования
#ifndef DLL_EXPORT
int main(int argc, char* argv[]) {
    printf("RedSand Monitoring Agent v1.0\n");
    printf("=============================\n\n");
    
    if (!InitializeAgent()) {
        printf("Ошибка инициализации агента\n");
        return 1;
    }
    
    printf("Агент запущен. Мониторинг процессов:\n\n");
    
    // Демонстрация мониторинга
    MonitorProcesses();
    
    printf("\nНажмите Enter для выхода...\n");
    getchar();
    
    StopAgent();
    
    return 0;
}
#endif
