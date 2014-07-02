//
//  Appscript.h
//  Appscript
//
//  Created by has on 02/07/2014.
//  Copyright (c) 2014 has. All rights reserved.
//

#import <Cocoa/Cocoa.h>

//! Project version number for Appscript.
FOUNDATION_EXPORT double AppscriptVersionNumber;

//! Project version string for Appscript.
FOUNDATION_EXPORT const unsigned char AppscriptVersionString[];

// In this header, you should import all the public headers of your framework using statements like #import <Appscript/PublicHeader.h>


// aem
#import "application.h"
#import "event.h"
#import "base.h"
#import "codecs.h"
#import "specifier.h"
#import "test.h"
#import "types.h"

// appscript base
#import "constant.h"
#import "appdata.h"
#import "command.h"
#import "reference.h"
#import "referencerenderer.h"

// misc
#import "sendthreadsafe.h"
#import "utils.h"
#import "objectrenderer.h"

// appscript bridge
#import "parser.h"
#import "terminology.h"
#import "bridgedata.h"