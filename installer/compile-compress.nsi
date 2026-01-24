; ========================================
; BTA Launcher NSIS Installer (Compressed)
; ========================================
; This version uses LZMA compression for smaller installer size.
; Build time is longer, but output is ~30% smaller.
; ========================================

!include "MUI2.nsh"

; --- Compression ---
SetCompressor /SOLID lzma
SetCompressorDictSize 64

; --- App Info ---
!define APPNAME "MeoLauncher"
!define APPVERSION "2.0.0"
!define APPEXE "MeoLauncher.exe"
!define INSTALLDIR "$LOCALAPPDATA\${APPNAME}"

; --- Installer Settings ---
Name "${APPNAME}"
OutFile "MeoLauncher Setup (Compressed).exe"
InstallDir "${INSTALLDIR}"
RequestExecutionLevel user

; --- Modern UI ---
!define MUI_ICON "..\app\assets\icon.ico"
!define MUI_UNICON "..\app\assets\icon.ico"
!define MUI_ABORTWARNING

; --- Pages ---
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; --- Language ---
!insertmacro MUI_LANGUAGE "English"

; ========================================
; Installation Section
; ========================================
Section "Install"
    SetOutPath "$INSTDIR"
    
    ; Copy all files from build output
    File /r "..\output-build\*.*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${APPEXE}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    CreateShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${APPEXE}"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Add to Programs and Features
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${APPVERSION}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "MeoLauncher"
SectionEnd

; ========================================
; Uninstall Section
; ========================================
Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APPNAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APPNAME}"
    
    ; Remove registry entries
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
