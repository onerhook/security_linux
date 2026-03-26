// RedSand Agent (C++) - Мониторинг поведения и перехват API
// Компиляция: g++ -o agent.exe agent.cpp -lws2_32 -static
// Запуск: От имени Администратора в изолированной среде

#include <windows.h>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <psapi.h>
#include <tlhelp32.h>

#pragma comment(lib, "psapi.lib")

using namespace std;

// Конфигурация
const string LOG_FILE = "logs/agent_activity.log";
const int MONITOR_DURATION_SEC = 10; // Время мониторинга

// Логирование событий
void LogEvent(const string& category, const string& action, const string& details) {
    ofstream log(LOG_FILE, ios::app);
    if (log.is_open()) {
        auto now = chrono::system_clock::now();
        auto time_t_now = chrono::system_clock::to_time_t(now);
        log << "[" << ctime(&time_t_now) << "] [" << category << "] " 
            << action << ": " << details << endl;
        log.close();
    }
    cout << "[AGENT] " << category << " -> " << action << endl;
}

// Получение списка процессов
vector<string> GetRunningProcesses() {
    vector<string> processes;
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot != INVALID_HANDLE_VALUE) {
        PROCESSENTRY32 pe32;
        pe32.dwSize = sizeof(PROCESSENTRY32);
        if (Process32First(hSnapshot, &pe32)) {
            do {
                processes.push_back(pe32.szExeFile);
            } while (Process32Next(hSnapshot, &pe32));
        }
        CloseHandle(hSnapshot);
    }
    return processes;
}

// Мониторинг создания процессов
void MonitorProcesses() {
    static vector<string> prevProcs = GetRunningProcesses();
    vector<string> currProcs = GetRunningProcesses();
    
    for (const auto& proc : currProcs) {
        bool found = false;
        for (const auto& prev : prevProcs) {
            if (proc == prev) { found = true; break; }
        }
        if (!found) {
            LogEvent("PROCESS", "NEW_PROCESS_CREATED", proc);
        }
    }
    prevProcs = currProcs;
}

// Простая эмуляция перехвата файловых операций (через polling目录)
// В продакшене использовать MinHook для перехвата CreateFileW
void MonitorFileSystem(const string& targetDir) {
    WIN32_FIND_DATA ffd;
    HANDLE hFind = FindFirstFile((targetDir + "\\*").c_str(), &ffd);
    if (hFind != INVALID_HANDLE_VALUE) {
        do {
            if (!(ffd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
                string fname = ffd.cFileName;
                if (fname.find(".encrypted") != string::npos || 
                    fname.find(".lock") != string::npos ||
                    fname.find("ransom") != string::npos) {
                    LogEvent("FILESYSTEM", "SUSPICIOUS_FILE_ACTIVITY", fname);
                }
            }
        } while (FindNextFile(hFind, &ffd) != 0);
        FindClose(hFind);
    }
}

// Проверка сетевых подключений (netstat парсинг)
void MonitorNetwork() {
    char buffer[4096];
    string cmd = "netstat -an | findstr ESTABLISHED";
    FILE* pipe = _popen(cmd.c_str(), "r");
    if (!pipe) return;
    
    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        string line(buffer);
        // Ищем подозрительные порты или IP
        if (line.find(":4444") != string::npos || // Metasploit default
            line.find(":8080") != string::npos || 
            line.find("192.168") != string::npos) {
            LogEvent("NETWORK", "SUSPICIOUS_CONNECTION", line);
        }
    }
    _pclose(pipe);
}

// Перехват вызовов реестра (упрощенно через проверку ключей автозагрузки)
void MonitorRegistry() {
    HKEY hKey;
    const char* runKey = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run";
    
    if (RegOpenKeyEx(HKEY_CURRENT_USER, runKey, 0, KEY_READ, &hKey) == ERROR_SUCCESS) {
        DWORD dwCount = 0;
        RegQueryInfoKey(hKey, NULL, NULL, NULL, &dwCount, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
        if (dwCount > 0) {
            LogEvent("REGISTRY", "PERSISTENCE_CHECK", "Run key has entries (check manually)");
        }
        RegCloseKey(hKey);
    }
}

int main(int argc, char* argv[]) {
    cout << "=== RedSand Agent v1.0 ===" << endl;
    cout << "Запуск мониторинга..." << endl;
    
    // Создание директории логов
    CreateDirectory("logs", NULL);
    
    LogEvent("SYSTEM", "AGENT_STARTED", "Monitoring initialized");
    
    auto startTime = chrono::steady_clock::now();
    
    while (true) {
        auto now = chrono::steady_clock::now();
        auto duration = chrono::duration_cast<chrono::seconds>(now - startTime).count();
        
        if (duration >= MONITOR_DURATION_SEC) {
            break;
        }
        
        MonitorProcesses();
        MonitorFileSystem(".");
        MonitorNetwork();
        MonitorRegistry();
        
        this_thread::sleep_for(chrono::milliseconds(500));
    }
    
    LogEvent("SYSTEM", "AGENT_STOPPED", "Monitoring finished");
    cout << "Анализ завершен. Логи сохранены в " << LOG_FILE << endl;
    
    return 0;
}
