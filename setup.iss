#define MyAppName "CS2Tracker"
#define MyAppVersion "latest"
#define MyAppPublisher "Jannik Novak"
#define MyAppURL "https://github.com/ashiven"
#define MyAppExeName "cs2tracker.exe"

[Setup]
AppId={{B3CA78AD-7671-4DF3-9FB3-5EDCA729E689}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}/{#MyAppName}
UninstallDisplayIcon={app}/{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
LicenseFile=LICENSE
PrivilegesRequired=lowest
OutputBaseFilename={#MyAppName}-setup
SetupIconFile=assets/icon.ico
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist/{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist/_internal/*"; DestDir: "{app}/_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}/{#MyAppName}"; Filename: "{app}/{#MyAppExeName}"
Name: "{autodesktop}/{#MyAppName}"; Filename: "{app}/{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}/{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
