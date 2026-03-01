$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath('Desktop')
$ShortcutPath = "$Desktop\PhotoOrganizer.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "C:\D\CAIE_tool\MyAIProduct\photo\android\run.bat"
$Shortcut.WorkingDirectory = "C:\D\CAIE_tool\MyAIProduct\photo\android"
$Shortcut.Description = "Photo Organizer - Android Test"
$Shortcut.Save()
Write-Host "Shortcut created: $ShortcutPath"
