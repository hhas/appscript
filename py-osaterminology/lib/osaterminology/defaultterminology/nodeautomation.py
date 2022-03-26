
types = [
		# Human-readable names for commonly used AE types.
		# Most of these names are equivalent to AS names, though
		# a few are adjusted to be more 'programmer friendly', 
		# e.g. 'float' instead of 'real', and a few have no AS equivalent,
		# e.g. 'UTF8Text'
		('anything', b'****'),
		
		('boolean', b'bool'),
		
		('shortInteger', b'shor'),
		('integer', b'long'),
		('unsignedInteger', b'magn'),
		('doubleInteger', b'comp'),
		("unsignedShortInteger", b'ushr'), # no AS keyword
		("unsignedInteger", b'magn'),
		("unsignedDoubleInteger", b'ucom'), # no AS keyword

		('fixed', b'fixd'),
		('longFixed', b'lfxd'),
		('decimalStruct', b'decm'),
		
		('smallReal', b'sing'),
		('real', b'doub'),
#		('extendedReal', b'exte'),
		('largeReal', b'ldbl'),
		
		('string', b'TEXT'),
		('UnicodeText', b'utxt'),
  		('UTF8Text', b'utf8'), # typeUTF8Text
		('UTF16Text', b'ut16'), # typeUTF16ExternalRepresentation
		
		('version', b'vers'),
		('date', b'ldt '),
		('list', b'list'),
		('record', b'reco'),
		('data', b'rdat'),
		('script', b'scpt'),
		
		('locationReference', b'insl'),
		('reference', b'obj '),
		
		('alias', b'alis'),
		('fileRef', b'fsrf'),
	#	('fileSpecification', b'fss '),
		('bookmarkData', b'bmrk'),
		('fileURL', b'furl'),
		
		('point', b'QDpt'),
		('boundingRectangle', b'qdrt'),
		('fixedPoint', b'fpnt'),
		('fixedRectangle', b'frct'),
		('longPoint', b'lpnt'),
		('longRectangle', b'lrct'),
		('longFixedPoint', b'lfpt'),
		('longFixedRectangle', b'lfrc'),
		
		('EPSPicture', b'EPS '),
		('GIFPicture', b'GIFf'),
		('JPEGPicture', b'JPEG'),
		('PICTPicture', b'PICT'),
		('TIFFPicture', b'TIFF'),
		('RGBColor', b'cRGB'),
		('RGB16Color', b'tr16'),
		('RGB96Color', b'tr96'),
		('graphicText', b'cgtx'),
		('colorTable', b'clrt'),
		('pixelMapRecord', b'tpmm'),
		
		('best', b'best'),
		('typeClass', b'type'),
		('constant', b'enum'),
		('property', b'prop'),
		
		# AEAddressDesc types
		
		('machPort', b'port'),
		('kernelProcessID', b'kpid'),
		('applicationBundleID', b'bund'),
		('processSerialNumber', b'psn '),
		('applicationSignature', b'sign'),
		('applicationURL', b'aprl'),
		
		# misc.
		
#		('missingValue', b'msng'),
		
		('null', b'null'),
		
		('machineLocation', b'mLoc'),
		('machine', b'mach'),
		
		('dashStyle', b'tdas'),
		('rotation', b'trot'),
		
		('item', b'cobj'),
		
		# month and weekday
		
		('January', b'jan '),
		('February', b'feb '),
		('March', b'mar '),
		('April', b'apr '),
		('May', b'may '),
		('June', b'jun '),
		('July', b'jul '),
		('August', b'aug '),
		('September', b'sep '),
		('October', b'oct '),
		('November', b'nov '),
		('December', b'dec '),
		
		('Sunday', b'sun '),
		('Monday', b'mon '),
		('Tuesday', b'tue '),
		('Wednesday', b'wed '),
		('Thursday', b'thu '),
		('Friday', b'fri '),
		('Saturday', b'sat '),
]


pseudotypes = [ # non-concrete types that are only used for documentation purposes; use to remap typesbycode
		('file', b'file'), # typically FileURL, but could be other file types as well
		('number', b'nmbr'), # any numerical type: Integer, Float, Long
		# ('text', b'ctxt'), # Word X, Excel X uses 'ctxt' instead of 'TEXT' or 'utxt' (TO CHECK: is this Excel's stupidity, or is it acceptable?)
]


properties = [
		('class', b'pcls'), # used as a key in AERecord structures that have a custom class; also some apps (e.g. Jaguar Finder) may omit it from their dictionaries despite using it
		('properties', b'pALL'),
		('id', b'ID  '), # some apps (e.g. iTunes) may omit 'id' property from terminology despite using it
]


elements = [
		('items', b'cobj'),
		('text', b'ctxt'),
]


enumerations = [
		('savo', [
				('yes', b'yes '), 
				('no', b'no  '), 
				('ask', b'ask '),
		]),
		# constants used in commands' 'ignore' argument (note: most apps currently ignore these):
		('cons', [
			('case', b'case'),
			('diacriticals', b'diac'),
			('expansion', b'expa'),
			('punctuation', b'punc'),
			('hyphens', b'hyph'),
			('whitespace', b'whit'),
			('numericStrings', b'nume'),
		]),
]


commands = [
	# required suite
	('run', b'aevtoapp', []),
	('open', b'aevtodoc', []),
	('print', b'aevtpdoc', []),
	('quit', b'aevtquit', [('saving', b'savo')]),
	# 'reopen' and 'activate' aren't listed in required suite, but should be
	('reopen', b'aevtrapp', []),
	('activate', b'miscactv', []),
	# 'launch' is a special case not listed in the required suite and implementation is provided by
	# the Apple event bridge (not the target applications), which uses the Process Manager/
	# LaunchServices to launch an application without sending it the usual run/open event.
	('launch', b'ascrnoop', []),
	# 'get' and 'set' commands are often omitted from applications' core suites, even when used
	('get', b'coregetd', []),
	('set', b'coresetd', [('to', b'data')]),
	# some apps (e.g. Safari) which support GetURL events may omit it from their terminology; 
	# 'open location' is the name Standard Additions defines for this event, so use it here
	('openLocation', b'GURLGURL', [('window', b'WIND')]), 
]
