ffprobe.exe -i $args[0] -show_frames -loglevel quiet |Select-String media_type=video -context 0,4 |foreach{$_.context.PostContext[3] -replace {.*=}} |Out-File $args[0].replace($args[1],"_ts.txt")