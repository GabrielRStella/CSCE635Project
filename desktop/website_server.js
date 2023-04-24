#!/usr/bin/env sh
"\"",`$(echo --% ' |out-null)" >$null;function :{};function dv{<#${/*'>/dev/null )` 2>/dev/null;dv() { #>
echo "1.31.3"; : --% ' |out-null <#';};v="$(dv)";d="$HOME/.deno/$v/bin/deno";if [ -x "$d" ];then exec "$d" run -q -A "$0" "$@";elif [ -f "$d" ];then chmod +x "$d" && exec "$d" run -q -A "$0" "$@";fi;bin_dir="$HOME/.deno/$v/bin";exe="$bin_dir/deno";has() { command -v "$1" >/dev/null; };if ! has unzip;then :;if ! has apt-get;then has brew && brew install unzip;else if [ "$(whoami)" = "root" ];then apt-get install unzip -y;elif has sudo;then echo "Can I install unzip for you? (its required for this command to work) ";read ANSWER;echo;if [ "$ANSWER" =~ ^[Yy] ];then sudo apt-get install unzip -y;fi;elif has doas;then echo "Can I install unzip for you? (its required for this command to work) ";read ANSWER;echo;if [ "$ANSWER" =~ ^[Yy] ];then doas apt-get install unzip -y;fi;fi;fi;fi;if ! has unzip;then echo "";echo "So I couldn't find an 'unzip' command";echo "And I tried to auto install it, but it seems that failed";echo "(This script needs unzip and either curl or wget)";echo "Please install the unzip command manually then re-run this script";exit 1;fi;if [ "$OS" = "Windows_NT" ];then target="x86_64-pc-windows-msvc";else :; case $(uname -sm) in "Darwin x86_64") target="x86_64-apple-darwin" ;; "Darwin arm64") target="aarch64-apple-darwin" ;; *) target="x86_64-unknown-linux-gnu" ;; esac;fi;deno_uri="https://github.com/denoland/deno/releases/download/v$v/deno-$target.zip";if [ ! -d "$bin_dir" ];then mkdir -p "$bin_dir";fi;if has curl;then curl --fail --location --progress-bar --output "$exe.zip" "$deno_uri";elif has wget;then wget --output-document="$exe.zip" "$deno_uri";else echo "Howdy! I looked for the 'curl' and for 'wget' commands but I didn't see either of them.";echo "Please install one of them";echo "Otherwise I have no way to install the missing deno version needed to run this code";fi;unzip -d "$bin_dir" -o "$exe.zip";chmod +x "$exe";rm "$exe.zip";exec "$d" run -q -A "$0" "$@"; #>}; $DenoInstall = "${HOME}/.deno/$(dv)"; $BinDir = "$DenoInstall/bin"; $DenoExe = "$BinDir/deno.exe"; if (-not(Test-Path -Path "$DenoExe" -PathType Leaf)) { $DenoZip = "$BinDir/deno.zip"; $DenoUri = "https://github.com/denoland/deno/releases/download/v$(dv)/deno-x86_64-pc-windows-msvc.zip"; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; if (!(Test-Path $BinDir)) { New-Item $BinDir -ItemType Directory | Out-Null; } Function Test-CommandExists { Param ($command); $oldPreference = $ErrorActionPreference; $ErrorActionPreference = "stop"; try {if(Get-Command "$command"){RETURN $true}} Catch {Write-Host "$command does not exist"; RETURN $false} Finally {$ErrorActionPreference=$oldPreference}; } if (Test-CommandExists curl) { curl -Lo $DenoZip $DenoUri; } else { curl.exe -Lo $DenoZip $DenoUri; } if (Test-CommandExists curl) { tar xf $DenoZip -C $BinDir; } else { tar.exe   xf $DenoZip -C $BinDir; } Remove-Item $DenoZip; $User = [EnvironmentVariableTarget]::User; $Path = [Environment]::GetEnvironmentVariable('Path', $User); if (!(";$Path;".ToLower() -like "*;$BinDir;*".ToLower())) { [Environment]::SetEnvironmentVariable('Path', "$Path;$BinDir", $User); $Env:Path += ";$BinDir"; } }; & "$DenoExe" run -q -A "$PSCommandPath" @args;
Exit $LastExitCode;
# */0
# }`;
echo here

# import { FileSystem } from "https://deno.land/x/quickr@0.6.20/main/file_system.js"
# import { run, Stderr, Stdout } from "https://deno.land/x/quickr@0.6.20/main/run.js"
# import * as yaml from "https://deno.land/std@0.168.0/encoding/yaml.ts"
# import archy from "https://deno.land/x/archaeopteryx@1.0.4/mod.ts"
# import { Console, clearAnsiStylesFrom, black, white, red, green, blue, yellow, cyan, magenta, lightBlack, lightWhite, lightRed, lightGreen, lightBlue, lightYellow, lightMagenta, lightCyan, blackBackground, whiteBackground, redBackground, greenBackground, blueBackground, yellowBackground, magentaBackground, cyanBackground, lightBlackBackground, lightRedBackground, lightGreenBackground, lightYellowBackground, lightBlueBackground, lightMagentaBackground, lightCyanBackground, lightWhiteBackground, bold, reset, dim, italic, underline, inverse, strikethrough, gray, grey, lightGray, lightGrey, grayBackground, greyBackground, lightGrayBackground, lightGreyBackground, } from "https://deno.land/x/quickr@0.6.21/main/console.js"

# const pathToProject = await FileSystem.walkUpUntil("config.yaml")
# const pathToConfig = `${pathToProject}/config.yaml`

# console.log("Here are your IP addresses\n")
# const chosenAddress = Console.askFor.oneOf(
#     Deno.networkInterfaces().filter((each)=>each.family=="IPv4").map((each)=>each.address),
#     "pick one and I'll update the config: "
# )

# let configContents = await FileSystem.read(pathToConfig)
# configContents = configContents.replace(/: .+# UNIQUE_ID_fo4i3jf84309583/, `: ${chosenAddress} # UNIQUE_ID_fo4i3jf84309583`)
# await FileSystem.write({
#     path: pathToConfig,
#     data: configContents,
# })

# var server = null
# var prevConfig = null
# var prevPathTo = null
# async function loadConfig() {
#     const info = yaml.parse(
#         await FileSystem.read(
#             pathToConfig
#         )
#     )
#     const config = info['(project)']['(profiles)']['(default)']
#     const pathTo = info['(project)']['(path_to)']

#     // if values that corrispond with the server were changed
#     if (
#         !prevConfig ||
#         prevConfig.desktop.file_server_port != config.desktop.file_server_port ||
#         prevPathTo.file_server_public_key != pathTo.file_server_public_key ||
#         prevPathTo.file_server_private_key != pathTo.file_server_private_key
#     ) {
#         if (server) {
#             server.close()
#         }
#         server = await archy({
#             root: "/",
#             port: config.desktop.file_server_port,
#             root: `${pathToProject}/desktop`,
#             cors: false,
#             secure: true,
#             certFile: `${pathToProject}/${pathTo.file_server_public_key}`,
#             keyFile: `${pathToProject}/${pathTo.file_server_private_key}`,
#         })
#     }
#     prevConfig = config
#     prevPathTo = pathTo
    
#     const htmlPath = `${pathToProject}/${pathTo.face_html}`
#     const htmlString = await FileSystem.read(htmlPath)
#     FileSystem.write({
#         path: htmlPath,
#         data: htmlString.replace(
#                 /:.+?\/\*UNQUE_ID_191093889137898240_address\*\//, `: ${JSON.stringify(config.desktop.ip_address)}/*UNQUE_ID_191093889137898240_address*/`
#             ).replace(
#                 /:.+?\/\*UNQUE_ID_19827378957898240_port\*\//, `: ${JSON.stringify(config.desktop.web_socket_port)}/*UNQUE_ID_19827378957898240_port*/`
#             )
#     })
# }

# // load at the begining and every time something changes
# loadConfig()
# for await (const event of Deno.watchFs(pathToConfig)) {
#     loadConfig()
# }