
tell application "ASDictionary"
	export {Â
		POSIX file "/System/Applications/Mail.app", Â
		POSIX file "/System/Applications/TextEdit.app", Â
		POSIX file "/System/Applications/Chess.app"} Â
		to (POSIX file "/Users/has/test") Â
		using file formats {plain text, single file HTML, frame based HTML} Â
		using styles {AppleScript, Python appscript, Ruby appscript} Â
		with compacting classes, showing hidden items and exporting to subfolders
end tell

