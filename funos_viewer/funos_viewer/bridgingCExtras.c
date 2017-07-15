//
//  bridgingCExtras.c
//  funos_viewer
//
//  Created by Bertrand Serlet on 5/11/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

#define static_assert(x, y)     // Somehow broken without this

#define __VPLOCAL_H__		// Hack to avoid importing platform/vplocal.h

#include <kv/ikv_viewer.h>

